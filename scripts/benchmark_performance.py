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
        window.__perfMapLoadMs = performance.now();
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
    project() { return window.__perfProjectOnScreen ? {x: 100, y: 100} : {x: -1, y: -1}; }
    queryRenderedFeatures(_bounds, options = {}) {
      const layer = options.layers && options.layers[0];
      return window.__perfBuildingFeatures && layer ? (window.__perfBuildingFeatures[layer] || []) : [];
    }
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
  window.__perfListCountMs = null;
  window.__perfFirstUsefulListMs = null;
  window.__perfMapLoadMs = null;
  window.__perfLoaderDismissMs = null;
  const observe = () => {
    const record = () => {
      const count = document.getElementById('coCount');
      if (window.__perfListCountMs === null && count && /^\d+ /.test(count.textContent || '')) {
        window.__perfListCountMs = performance.now();
      }
      const loader = document.getElementById('loader');
      if (window.__perfLoaderDismissMs === null && loader && loader.classList.contains('done')) {
        window.__perfLoaderDismissMs = performance.now();
      }
    };
    new MutationObserver(record).observe(document.documentElement, {subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ['class']});
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
        if url.startswith("http://127.0.0.1:"):
            route.fallback()
            return
        external_requests.append(url)
        if "maplibre-gl.js" in url:
            route.fulfill(status=200, content_type="application/javascript", body=MAPLIBRE_STUB)
        elif "maplibre-gl.css" in url or "fonts.googleapis.com" in url:
            route.fulfill(status=200, content_type="text/css", body="")
        else:
            route.abort()

    context.route("**/*", route_external)


def wait_for_list(page: Page) -> None:
    page.wait_for_function("window.__perfListCountMs !== null", timeout=10_000)
    counts = page.evaluate(
        """async () => {
          await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
          const counts = {
            label: parseInt(document.getElementById('coCount').textContent, 10),
            rows: document.querySelectorAll('.co').length,
            markers: document.querySelectorAll('.co-marker').length,
          };
          window.__perfFirstUsefulListMs = performance.now();
          return counts;
        }"""
    )
    if not counts["label"] or counts["label"] != counts["rows"] or counts["rows"] != counts["markers"]:
        raise RuntimeError(f"first useful list is inconsistent: {counts}")


class NetworkRecorder:
    def __init__(self, session) -> None:
        self.responses: dict[str, dict[str, object]] = {}
        self.extra_status: dict[str, int] = {}
        self.finished_bytes: dict[str, int] = {}
        session.on("Network.responseReceived", self._response_received)
        session.on("Network.responseReceivedExtraInfo", self._extra_info)
        session.on("Network.loadingFinished", self._loading_finished)
        session.send("Network.enable")

    def reset(self) -> None:
        self.responses.clear()
        self.extra_status.clear()
        self.finished_bytes.clear()

    def _response_received(self, event: dict[str, object]) -> None:
        self.responses[str(event["requestId"])] = dict(event["response"])

    def _extra_info(self, event: dict[str, object]) -> None:
        self.extra_status[str(event["requestId"])] = int(event["statusCode"])

    def _loading_finished(self, event: dict[str, object]) -> None:
        self.finished_bytes[str(event["requestId"])] = int(event.get("encodedDataLength", 0))

    def summarize(self, origin: str) -> dict[str, object]:
        entries = []
        for request_id, response in self.responses.items():
            url = str(response.get("url", ""))
            if not url.startswith(origin):
                continue
            entries.append({
                "url": url,
                "status": self.extra_status.get(request_id, int(response.get("status", 0))),
                "transfer_bytes": self.finished_bytes.get(request_id, int(response.get("encodedDataLength", 0))),
                "from_disk_cache": bool(response.get("fromDiskCache", False)),
                "from_prefetch_cache": bool(response.get("fromPrefetchCache", False)),
            })
        statuses: dict[str, int] = {}
        for entry in entries:
            key = str(entry["status"])
            statuses[key] = statuses.get(key, 0) + 1
        return {
            "request_count": len(entries),
            "transfer_bytes": sum(int(entry["transfer_bytes"]) for entry in entries),
            "status_counts": statuses,
            "disk_cache_hits": sum(bool(entry["from_disk_cache"]) for entry in entries),
            "prefetch_cache_hits": sum(bool(entry["from_prefetch_cache"]) for entry in entries),
            "responses": entries,
        }


def final_navigation_network(
    network: NetworkRecorder, origin: str, navigation: str
) -> dict[str, object]:
    """Return the completed navigation summary after enforcing one request per dataset."""
    summary = network.summarize(origin)
    responses = summary["responses"]
    for filename in ("companies.json", "ticker.json"):
        matching = [
            response
            for response in responses
            if response["url"].split("?", 1)[0].endswith("/" + filename)
        ]
        if len(matching) != 1:
            raise RuntimeError(
                f"expected one {filename} request in completed {navigation}: {summary}"
            )
    return summary


def read_load_sample(
    page: Page,
    mode: str,
    run: int,
    errors: list[str],
) -> dict[str, object]:
    page.wait_for_timeout(50)
    metrics = page.evaluate(
        """({mode, run}) => ({
          mode,
          run,
          first_useful_list_ms: window.__perfFirstUsefulListMs,
          list_count_ready_ms: window.__perfListCountMs,
          map_load_ms: window.__perfMapLoadMs,
          list_before_map_load: window.__perfMapLoadMs === null || window.__perfFirstUsefulListMs < window.__perfMapLoadMs,
          loader_dismiss_ms: window.__perfLoaderDismissMs,
          content_ready_before_map_load: window.__perfLoaderDismissMs !== null &&
            (window.__perfMapLoadMs === null || window.__perfLoaderDismissMs < window.__perfMapLoadMs),
          visible_rows: document.querySelectorAll('.co').length,
          marker_count: document.querySelectorAll('.co-marker').length,
        })""",
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
        "stable_set_data_detected": any(source["calls"] for source in sources.values()),
        "repeated_set_data_detected": any(source["repeated_payload_calls"] for source in sources.values()),
    }


def building_source_invalidation(page: Page, company: dict[str, object]) -> dict[str, object]:
    """Verify one real geometry write, a stable skip, and a removal write."""
    page.evaluate(
        """company => {
          const d = 0.0002;
          const ring = [
            [company.lng - d, company.lat - d],
            [company.lng + d, company.lat - d],
            [company.lng + d, company.lat + d],
            [company.lng - d, company.lat + d],
            [company.lng - d, company.lat - d],
          ];
          const feature = {
            type: 'Feature',
            geometry: {type: 'Polygon', coordinates: [ring]},
            properties: {render_height: 12, render_min_height: 0},
          };
          window.__perfProjectOnScreen = true;
          window.__perfBuildingFeatures = {'building-3d': [feature], building: [feature]};
          window.__perfMap.zoom = 14;
          Object.values(window.__perfMap.sources).forEach(source => {
            source.calls = 0;
            source.repeatedCalls = 0;
          });
        }""",
        company,
    )

    def settle_and_read() -> dict[str, dict[str, int]]:
        page.evaluate("window.__perfMap.emit('idle')")
        page.wait_for_timeout(180)
        return page.evaluate(
            """() => Object.fromEntries(Object.entries(window.__perfMap.sources).map(([id, source]) => [id, {
              calls: source.calls,
              repeated_payload_calls: source.repeatedCalls,
              features: source.data.features.length,
            }]))"""
        )

    first_geometry = settle_and_read()
    page.evaluate("Object.values(window.__perfMap.sources).forEach(source => { source.calls = 0; source.repeatedCalls = 0; })")
    stable_geometry = settle_and_read()
    page.evaluate(
        """() => {
          window.__perfBuildingFeatures = {'building-3d': [], building: []};
          Object.values(window.__perfMap.sources).forEach(source => { source.calls = 0; source.repeatedCalls = 0; });
        }"""
    )
    removed_geometry = settle_and_read()
    valid = all(
        first_geometry[source_id]["calls"] == 1
        and first_geometry[source_id]["features"] == 1
        and stable_geometry[source_id]["calls"] == 0
        and removed_geometry[source_id]["calls"] == 1
        and removed_geometry[source_id]["features"] == 0
        for source_id in ("co-buildings-3d", "co-buildings-2d")
    )
    if not valid:
        raise RuntimeError(
            f"building source invalidation failed: first={first_geometry}, "
            f"stable={stable_geometry}, removed={removed_geometry}"
        )
    return {
        "first_geometry": first_geometry,
        "stable_geometry": stable_geometry,
        "removed_geometry": removed_geometry,
        "all_transitions_valid": True,
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


def read_consistent_count(page: Page) -> int:
    """Read a settled result count after checking the rendered rows and markers."""
    counts = page.evaluate(
        """async () => {
          await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
          return {
            label: parseInt(document.getElementById('coCount').textContent, 10),
            rows: document.querySelectorAll('.co').length,
            markers: document.querySelectorAll('.co-marker').length,
          };
        }"""
    )
    if counts["label"] != counts["rows"] or counts["rows"] != counts["markers"]:
        raise RuntimeError(f"application count is inconsistent: {counts}")
    return int(counts["label"])


def expected_counts_from_app(browser, url: str, map_delay_ms: int) -> dict[str, int]:
    """Exercise the real controls once outside timed samples to derive expectations."""
    context = browser.new_context(locale="es-PE", viewport={"width": 1280, "height": 800})
    configure_context(context, map_delay_ms, [])
    page = context.new_page()
    network = NetworkRecorder(context.new_cdp_session(page))
    try:
        network.reset()
        page.goto(url, wait_until="load")
        wait_for_list(page)
        page.wait_for_function("window.__perfMapLoadMs !== null", timeout=10_000)
        counts = {"initial_ecosystem": read_consistent_count(page)}
        page.evaluate("document.querySelector('[data-view-category=\"Coworking Space\"]').click()")
        counts["ecosystem_with_coworking"] = read_consistent_count(page)
        page.evaluate("document.querySelector('[data-view-mode=\"remote\"]').click()")
        counts["remote_all_types"] = read_consistent_count(page)
        page.evaluate("document.querySelector('[data-workspace-type=\"cafe\"]').click()")
        counts["remote_without_cafe"] = read_consistent_count(page)
        page.wait_for_timeout(50)
        final_navigation_network(network, url, "expected-counts navigation")
        return counts
    finally:
        context.close()


def git_stdout(*args: str) -> str | None:
    """Return a Git value when repository metadata is available."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def summarize_interactions(samples: list[dict[str, float]]) -> dict[str, object]:
    return {
        "handler": summarize([sample["handler_ms"] for sample in samples]),
        "settled_after_two_frames": summarize([sample["settled_ms"] for sample in samples]),
    }


def run_benchmark(
    runs: int,
    map_delay_ms: int,
    require_no_repeated_set_data: bool = False,
    require_list_before_map_load: bool = False,
    trace_path: Path | None = None,
    trace_versioned: bool = False,
) -> dict[str, object]:
    companies_path = ROOT / "companies.json"
    companies = json.loads(companies_path.read_text(encoding="utf-8"))
    geometry_company = next(
        company for company in companies
        if company.get("city") == "lima"
        and company.get("workspace_type") in {"coworking", "library"}
        and company.get("sources")
    )
    git_head = git_stdout("rev-parse", "HEAD")
    comparison_base = git_stdout("merge-base", "origin/master", "HEAD")
    interaction_runs: dict[str, list[dict[str, float]]] = {
        "ecosystem_add_coworking": [],
        "switch_to_remote": [],
        "remote_remove_cafe": [],
    }
    external_requests: list[str] = []
    cold: list[dict[str, object]] = []
    warm: list[dict[str, object]] = []
    idle_writes: dict[str, object] | None = None
    building_invalidation: dict[str, object] | None = None

    with local_server() as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        chromium_version = browser.version
        counts = expected_counts_from_app(browser, url, map_delay_ms)
        for run in range(1, runs + 1):
            context = browser.new_context(locale="es-PE", viewport={"width": 1280, "height": 800})
            run_external_requests: list[str] = []
            configure_context(context, map_delay_ms, run_external_requests)
            page = context.new_page()
            network = NetworkRecorder(context.new_cdp_session(page))
            errors: list[str] = []
            page.on("pageerror", lambda error, sink=errors: sink.append(str(error)))
            network.reset()
            page.goto(url, wait_until="load")
            wait_for_list(page)
            page.wait_for_function("window.__perfMapLoadMs !== null", timeout=10_000)
            cold.append(read_load_sample(page, "cold", run, list(errors)))
            if cold[-1]["visible_rows"] != counts["initial_ecosystem"]:
                raise RuntimeError(f"initial result count does not match application contract: {cold[-1]}")
            cold[-1]["first_party_network"] = final_navigation_network(
                network, url, f"cold run {run}"
            )

            error_start = len(errors)
            network.reset()
            page.reload(wait_until="load")
            wait_for_list(page)
            page.wait_for_function("window.__perfMapLoadMs !== null", timeout=10_000)
            warm.append(read_load_sample(page, "warm", run, errors[error_start:]))
            if warm[-1]["visible_rows"] != counts["initial_ecosystem"]:
                raise RuntimeError(f"warm result count does not match application contract: {warm[-1]}")
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
                building_invalidation = building_source_invalidation(page, geometry_company)

            warm[-1]["first_party_network"] = final_navigation_network(
                network, url, f"warm run {run}"
            )

            external_requests.extend(run_external_requests)
            context.close()

        if trace_path:
            trace_path.parent.mkdir(parents=True, exist_ok=True)
            trace_context = browser.new_context(locale="es-PE", viewport={"width": 1280, "height": 800})
            configure_context(trace_context, map_delay_ms, [])
            trace_context.tracing.start(screenshots=True, snapshots=True, sources=True)
            trace_page = trace_context.new_page()
            trace_network = NetworkRecorder(trace_context.new_cdp_session(trace_page))
            trace_network.reset()
            trace_page.goto(url, wait_until="load")
            wait_for_list(trace_page)
            trace_page.wait_for_function("window.__perfMapLoadMs !== null", timeout=10_000)
            measure_click(trace_page, '[data-view-category="Coworking Space"]', counts["ecosystem_with_coworking"])
            measure_click(trace_page, '[data-view-mode="remote"]', counts["remote_all_types"])
            measure_click(trace_page, '[data-workspace-type="cafe"]', counts["remote_without_cafe"])
            stable_idle_writes(trace_page)
            final_navigation_network(trace_network, url, "trace navigation")
            trace_context.tracing.stop(path=str(trace_path))
            trace_context.close()
        browser.close()

    if idle_writes is None:
        raise RuntimeError("building-source detector was not exercised")
    if building_invalidation is None:
        raise RuntimeError("building-source invalidation was not exercised")
    if require_no_repeated_set_data and idle_writes["stable_set_data_detected"]:
        raise RuntimeError(f"repeated stable-view setData calls detected: {idle_writes}")
    if require_list_before_map_load and not all(
        bool(sample["list_before_map_load"]) and bool(sample["content_ready_before_map_load"])
        for sample in cold + warm
    ):
        raise RuntimeError("the usable list and dismissed loader did not precede the synthetic map load")
    all_errors = [error for sample in cold + warm for error in sample["page_errors"]]
    if all_errors:
        raise RuntimeError(f"browser page errors detected: {all_errors}")
    tile_requests = sorted({url for url in external_requests if "openfreemap.org" in url})
    if tile_requests:
        raise RuntimeError(f"public tile requests escaped the deterministic map stub: {tile_requests}")

    dataset_hash = hashlib.sha256(companies_path.read_bytes()).hexdigest()
    trace_artifact = None
    if trace_path:
        trace_artifact = {
            "filename": trace_path.name,
            "sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
            "excluded_from_timings": True,
            "versioned": trace_versioned,
        }
    result = {
        "schema_version": 1,
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "git": {
            "repository_head": git_head,
            "comparison_base": comparison_base,
            "index_sha256": hashlib.sha256((ROOT / "index.html").read_bytes()).hexdigest(),
            "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
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
            "cold_first_useful_list": summarize([float(sample["first_useful_list_ms"]) for sample in cold]),
            "warm_first_useful_list": summarize([float(sample["first_useful_list_ms"]) for sample in warm]),
        },
        "interactions": {
            scenario: summarize_interactions(samples) for scenario, samples in interaction_runs.items()
        },
        "correctness": {"expected_counts": counts, "all_samples_valid": True},
        "stable_view_building_source_writes": idle_writes,
        "building_source_invalidation": building_invalidation,
        "network": {
            "external_requests_blocked_or_stubbed": len(external_requests),
            "external_hosts": sorted({url.split("/", 3)[2] for url in external_requests}),
            "public_tile_requests": tile_requests,
        },
        "trace_artifact": trace_artifact,
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
    parser.add_argument("--trace", type=Path, help="Trace diagnóstico separado de las muestras")
    parser.add_argument(
        "--trace-versioned",
        action="store_true",
        help="Declara que el trace se añadirá al repositorio junto al resultado",
    )
    parser.add_argument("--require-no-repeated-set-data", action="store_true")
    parser.add_argument("--require-list-before-map-load", action="store_true")
    args = parser.parse_args()
    if args.runs < 1 or args.map_delay_ms < 0:
        parser.error("--runs must be positive and --map-delay-ms cannot be negative")

    trace_path = None
    if args.trace:
        trace_path = args.trace if args.trace.is_absolute() else ROOT / args.trace
    if args.trace_versioned:
        if trace_path is None:
            parser.error("--trace-versioned requires --trace")
        try:
            trace_path.relative_to(ROOT)
        except ValueError:
            parser.error("--trace-versioned requires a trace path inside the repository")
    result = run_benchmark(
        args.runs,
        args.map_delay_ms,
        args.require_no_repeated_set_data,
        args.require_list_before_map_load,
        trace_path,
        args.trace_versioned,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
