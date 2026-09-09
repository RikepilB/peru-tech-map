"""Línea base reproducible del navegador sin depender de tiles públicos.

Sirve los archivos reales por HTTP, sustituye únicamente MapLibre por un doble determinista y
mide cinco cargas frías, cinco recargas calientes, cambios de filtros y escrituras GeoJSON en
cinco ciclos ``idle`` equivalentes. No representa el tiempo de descarga o render WebGL real.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import threading
from typing import Iterator

from playwright.sync_api import BrowserContext, Page, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS = 5
DEFAULT_MAP_DELAY_MS = 200


MAPLIBRE_STUB = r"""
(() => {
  class FakeMap {
    constructor(options) {
      this.handlers = {};
      this.onceHandlers = {};
      this.sources = {};
      this.layers = new globalThis.Map();
      this.center = {lng: options.center[0], lat: options.center[1]};
      this.zoom = options.zoom;
      this.bearing = options.bearing || 0;
      this.canvas = document.createElement('canvas');
      this.canvas.width = 1024;
      this.canvas.height = 768;
      this.canvas.style.width = '1024px';
      this.canvas.style.height = '768px';
      document.getElementById(options.container).appendChild(this.canvas);
      window.__perfMap = this;
      setTimeout(() => {
        this.emit('load');
        setTimeout(() => this.emit('idle'), 20);
      }, window.__PERF_MAP_DELAY_MS || 0);
    }
    on(event, layerOrHandler, maybeHandler) {
      const handler = typeof layerOrHandler === 'function' ? layerOrHandler : maybeHandler;
      (this.handlers[event] ||= []).push(handler);
      return this;
    }
    once(event, handler) {
      (this.onceHandlers[event] ||= []).push(handler);
      return this;
    }
    emit(event, payload = {}) {
      for (const handler of this.handlers[event] || []) handler(payload);
      const once = this.onceHandlers[event] || [];
      this.onceHandlers[event] = [];
      for (const handler of once) handler(payload);
    }
    getStyle() { return {layers: []}; }
    getLayer(id) { return this.layers.get(id) || null; }
    addLayer(layer) { this.layers.set(layer.id, layer); }
    addSource(id, definition) {
      const source = {
        data: definition.data,
        calls: 0,
        repeatedCalls: 0,
        lastPayload: null,
        setData: data => {
          const payload = JSON.stringify(data);
          source.calls += 1;
          if (source.lastPayload === payload) source.repeatedCalls += 1;
          source.lastPayload = payload;
          source.data = data;
        },
      };
      this.sources[id] = source;
    }
    getSource(id) { return this.sources[id] || null; }
    getCanvas() { return this.canvas; }
    getCenter() { return this.center; }
    getBearing() { return this.bearing; }
    getZoom() { return this.zoom; }
    project() { return {x: -1, y: -1}; }
    queryRenderedFeatures() { return []; }
    setPaintProperty() {}
    setLayoutProperty() {}
    setFilter() {}
    setLayerZoomRange() {}
    setSky() {}
    setFeatureState() {}
    setMaxBounds() {}
    setMinZoom() {}
    flyTo(options) {
      if (options.center) this.center = {lng: options.center[0], lat: options.center[1]};
      if (options.zoom) this.zoom = options.zoom;
    }
    easeTo(options) { if (typeof options.bearing === 'number') this.bearing = options.bearing; }
    zoomIn() {}
    zoomOut() {}
  }

  class FakeMarker {
    constructor(options) { this.element = options.element; }
    setLngLat() { return this; }
    addTo() { document.getElementById('map').appendChild(this.element); return this; }
    remove() { this.element.remove(); }
  }

  class FakePopup {
    setLngLat() { return this; }
    setHTML() { return this; }
    addTo() { return this; }
    remove() {}
  }

  window.maplibregl = {Map: FakeMap, Marker: FakeMarker, Popup: FakePopup};
})();
"""


INIT_SCRIPT = r"""
delay => {
  window.__PERF_MAP_DELAY_MS = delay;
  window.__perfFirstListMs = null;
  const observe = () => {
    const record = () => {
      const count = document.getElementById('coCount');
      if (window.__perfFirstListMs === null && count && /^\d+ /.test(count.textContent || '')) {
        window.__perfFirstListMs = performance.now();
      }
    };
    new MutationObserver(record).observe(document.documentElement, {subtree: true, childList: true, characterData: true});
    record();
  };
  if (document.documentElement) observe();
  else document.addEventListener('DOMContentLoaded', observe, {once: true});
}
"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


@contextmanager
def local_server() -> Iterator[str]:
    handler = partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def configure_context(context: BrowserContext, map_delay_ms: int, external_requests: list[str]) -> None:
    context.add_init_script(f"({INIT_SCRIPT})({map_delay_ms});")

    def route_external(route) -> None:
        url = route.request.url
        external_requests.append(url)
        if "maplibre-gl.js" in url:
            route.fulfill(status=200, content_type="application/javascript", body=MAPLIBRE_STUB)
        elif "maplibre-gl.css" in url or "fonts.googleapis.com" in url:
            route.fulfill(status=200, content_type="text/css", body="")
        else:
            route.abort()

    context.route("https://**/*", route_external)


def wait_for_list(page: Page) -> None:
    page.wait_for_function("window.__perfFirstListMs !== null", timeout=10_000)
    page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
    counts = page.evaluate(
        "() => ({label: parseInt(document.getElementById('coCount').textContent, 10), rows: document.querySelectorAll('.co').length, markers: document.querySelectorAll('.co-marker').length})"
    )
    if not counts["label"] or counts["label"] != counts["rows"] or counts["rows"] != counts["markers"]:
        raise RuntimeError(f"first useful list is inconsistent: {counts}")


def read_load_sample(page: Page, mode: str, run: int, errors: list[str]) -> dict[str, object]:
    metrics = page.evaluate(
        """
        ({mode, run}) => {
          const resources = performance.getEntriesByType('resource')
            .filter(entry => entry.name.startsWith(location.origin));
          return {
            mode,
            run,
            first_list_ms: window.__perfFirstListMs,
            visible_rows: document.querySelectorAll('.co').length,
            marker_count: document.querySelectorAll('.co-marker').length,
            same_origin_requests: resources.length,
            same_origin_transfer_bytes: resources.reduce((sum, entry) => sum + (entry.transferSize || 0), 0),
            same_origin_body_bytes: resources.reduce((sum, entry) => sum + (entry.encodedBodySize || 0), 0),
          };
        }
        """,
        {"mode": mode, "run": run},
    )
    metrics["page_errors"] = errors
    return metrics


def measure_click(page: Page, selector: str, expected_count: int) -> dict[str, float]:
    measurement = page.evaluate(
        """
        async ({selector, expected}) => {
          const control = document.querySelector(selector);
          const start = performance.now();
          control.click();
          const handlerDone = performance.now();
          await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
          const rows = document.querySelectorAll('.co').length;
          const markers = document.querySelectorAll('.co-marker').length;
          const label = parseInt(document.getElementById('coCount').textContent, 10);
          if (rows !== expected || markers !== expected || label !== expected) {
            throw new Error(`expected ${expected} results; saw label=${label}, rows=${rows}, markers=${markers}`);
          }
          return {handler_ms: handlerDone - start, settled_ms: performance.now() - start};
        }
        """,
        {"selector": selector, "expected": expected_count},
    )
    return {key: float(value) for key, value in measurement.items()}


def stable_idle_writes(page: Page, idle_events: int = 5) -> dict[str, object]:
    # Seed the last payload, then preserve it while resetting counters.
    page.evaluate("window.__perfMap.emit('idle')")
    page.wait_for_timeout(180)
    page.evaluate(
        """() => Object.values(window.__perfMap.sources).forEach(source => {
          source.calls = 0;
          source.repeatedCalls = 0;
        })"""
    )
    for _ in range(idle_events):
        page.evaluate("window.__perfMap.emit('idle')")
        page.wait_for_timeout(180)
    sources = page.evaluate(
        """() => Object.fromEntries(Object.entries(window.__perfMap.sources).map(([id, source]) => [id, {
          calls: source.calls,
          repeated_payload_calls: source.repeatedCalls,
        }]))"""
    )
    return {
        "stable_idle_events": idle_events,
        "sources": sources,
        "repeated_set_data_detected": any(source["repeated_payload_calls"] for source in sources.values()),
    }


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return ordered[index]


def summarize(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_ms": round(median, 3),
        "mad_ms": round(statistics.median(abs(value - median) for value in values), 3),
        "p95_ms": round(percentile(values, 0.95), 3),
        "min_ms": round(min(values), 3),
        "max_ms": round(max(values), 3),
    }


def file_bytes() -> dict[str, int]:
    return {name: (ROOT / name).stat().st_size for name in ("index.html", "companies.json", "ticker.json")}


def expected_counts(companies: list[dict[str, object]]) -> dict[str, int]:
    lima = [company for company in companies if company.get("city") == "lima"]
    ecosystem = {"Startup", "Technology Consultancy"}
    return {
        "initial_ecosystem": sum(company.get("category") in ecosystem for company in lima),
        "ecosystem_with_coworking": sum(
            company.get("category") in ecosystem | {"Coworking Space"} for company in lima
        ),
        "remote_all_types": sum(
            company.get("workspace_type") in {"coworking", "cafe", "library"} and bool(company.get("sources"))
            for company in lima
        ),
        "remote_without_cafe": sum(
            company.get("workspace_type") in {"coworking", "library"} and bool(company.get("sources"))
            for company in lima
        ),
    }


def summarize_interactions(samples: list[dict[str, float]]) -> dict[str, object]:
    return {
        "handler": summarize([sample["handler_ms"] for sample in samples]),
        "settled_after_two_frames": summarize([sample["settled_ms"] for sample in samples]),
    }


def run_benchmark(runs: int, map_delay_ms: int, require_no_repeated_set_data: bool = False) -> dict[str, object]:
    companies_path = ROOT / "companies.json"
    companies = json.loads(companies_path.read_text(encoding="utf-8"))
    counts = expected_counts(companies)
    interaction_runs: dict[str, list[dict[str, float]]] = {
        "ecosystem_add_coworking": [],
        "switch_to_remote": [],
        "remote_remove_cafe": [],
    }
    external_requests: list[str] = []
    cold: list[dict[str, object]] = []
    warm: list[dict[str, object]] = []
    idle_writes: dict[str, object] | None = None

    with local_server() as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        chromium_version = browser.version
        for run in range(1, runs + 1):
            context = browser.new_context(locale="es-PE", viewport={"width": 1280, "height": 800})
            run_external_requests: list[str] = []
            configure_context(context, map_delay_ms, run_external_requests)
            page = context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(url, wait_until="load")
            wait_for_list(page)
            cold.append(read_load_sample(page, "cold", run, list(errors)))

            error_start = len(errors)
            page.reload(wait_until="load")
            wait_for_list(page)
            warm.append(read_load_sample(page, "warm", run, errors[error_start:]))

            interaction_runs["ecosystem_add_coworking"].append(measure_click(
                page, '[data-view-category="Coworking Space"]', counts["ecosystem_with_coworking"]
            ))
            interaction_runs["switch_to_remote"].append(measure_click(
                page, '[data-view-mode="remote"]', counts["remote_all_types"]
            ))
            interaction_runs["remote_remove_cafe"].append(measure_click(
                page, '[data-workspace-type="cafe"]', counts["remote_without_cafe"]
            ))
            if run == runs:
                idle_writes = stable_idle_writes(page)

            external_requests.extend(run_external_requests)
            context.close()
        browser.close()

    if idle_writes is None:
        raise RuntimeError("building-source detector was not exercised")
    if require_no_repeated_set_data and idle_writes["repeated_set_data_detected"]:
        raise RuntimeError(f"repeated stable-view setData calls detected: {idle_writes}")
    all_errors = [error for sample in cold + warm for error in sample["page_errors"]]
    if all_errors:
        raise RuntimeError(f"browser page errors detected: {all_errors}")
    tile_requests = sorted({url for url in external_requests if "openfreemap.org" in url})
    if tile_requests:
        raise RuntimeError(f"public tile requests escaped the deterministic map stub: {tile_requests}")

    dataset_hash = hashlib.sha256(companies_path.read_bytes()).hexdigest()
    git_head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    result = {
        "schema_version": 1,
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "git": {
            "subject_commit": git_head,
            "index_sha256": hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest(),
        },
        "environment": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "logical_cpus": os.cpu_count(),
            "python": platform.python_version(),
            "playwright": version("playwright"),
            "browser": f"playwright-chromium-{chromium_version}-headless",
            "viewport": [1280, 800],
            "locale": "es-PE",
        },
        "dataset": {"companies": len(companies), "sha256": dataset_hash, "file_bytes": file_bytes()},
        "protocol": {
            "runs_per_load_mode": runs,
            "cold": "first navigation in a new BrowserContext",
            "warm": "immediate reload in the same BrowserContext",
            "first_useful_list": "numeric count equals rows and markers, followed by two animation frames",
            "synthetic_map_load_delay_ms": map_delay_ms,
            "public_network": "blocked; MapLibre replaced by deterministic local stub",
        },
        "loads": {
            "cold": cold,
            "warm": warm,
            "cold_first_list": summarize([float(sample["first_list_ms"]) for sample in cold]),
            "warm_first_list": summarize([float(sample["first_list_ms"]) for sample in warm]),
        },
        "interactions": {
            scenario: summarize_interactions(samples) for scenario, samples in interaction_runs.items()
        },
        "correctness": {"expected_counts": counts, "all_samples_valid": True},
        "stable_view_building_source_writes": idle_writes,
        "network": {
            "external_requests_blocked_or_stubbed": len(external_requests),
            "external_hosts": sorted({url.split("/", 3)[2] for url in external_requests}),
            "public_tile_requests": tile_requests,
        },
        "limitations": [
            "The fixed map delay isolates application scheduling; it is not a production tile benchmark.",
            "Playwright timing on this host is useful for before/after comparisons on the same host only.",
            "External logos, fonts, MapLibre, styles and tiles are excluded from transfer byte totals.",
        ],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--map-delay-ms", type=int, default=DEFAULT_MAP_DELAY_MS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-no-repeated-set-data", action="store_true")
    args = parser.parse_args()
    if args.runs < 1 or args.map_delay_ms < 0:
        parser.error("--runs must be positive and --map-delay-ms cannot be negative")

    result = run_benchmark(args.runs, args.map_delay_ms, args.require_no_repeated_set_data)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
