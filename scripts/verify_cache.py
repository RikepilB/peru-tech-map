"""Verify PeruGrid's mutable-resource cache contract without retaining bodies."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Callable
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://www.perugrid.com"
DEFAULT_PATHS = ("/", "/index.html", "/companies.json", "/ticker.json")
REQUIRED_CACHE_DIRECTIVES = {"public", "max-age=0", "must-revalidate"}
MAX_RESPONSE_BYTES = 15 * 1024 * 1024


class CacheContractError(ValueError):
    """A response or revision violates the public cache contract."""


@dataclass(frozen=True)
class CacheResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    final_url: str | None = None


def _headers(values) -> dict[str, str]:
    return {str(key).casefold(): str(value) for key, value in values.items()}


def _cache_directives(value: str) -> set[str]:
    return {part.strip().casefold() for part in value.split(",") if part.strip()}


def _json_digest(value) -> str:
    canonical = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _verify_json(path: str, body: bytes) -> tuple[list, str] | None:
    if not path.endswith(".json"):
        return None
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CacheContractError(f"{path}: response is not valid UTF-8 JSON") from exc
    if not isinstance(payload, list):
        raise CacheContractError(f"{path}: top-level value must be an array")
    return payload, _json_digest(payload)


def probe_resources(
    fetch: Callable[[str, str | None], CacheResponse],
    *,
    paths: tuple[str, ...] = DEFAULT_PATHS,
    expected_absent_site_ids: set[str] | None = None,
    expected_absent_names: set[str] | None = None,
    require_vercel: bool = False,
) -> dict[str, dict]:
    """Check 200, stable replay and conditional 304 for every mutable path."""
    results = {}
    for path in paths:
        initial = fetch(path, None)
        headers = _headers(initial.headers)
        if initial.status != 200:
            raise CacheContractError(f"{path}: expected 200, received {initial.status}")
        if len(initial.body) > MAX_RESPONSE_BYTES:
            raise CacheContractError(f"{path}: response exceeds 15 MiB")
        etag = headers.get("etag")
        if not etag:
            raise CacheContractError(f"{path}: ETag is required")
        directives = _cache_directives(headers.get("cache-control", ""))
        if directives != REQUIRED_CACHE_DIRECTIVES:
            raise CacheContractError(
                f"{path}: Cache-Control must be exactly "
                f"{', '.join(sorted(REQUIRED_CACHE_DIRECTIVES))}"
            )
        if require_vercel and not headers.get("x-vercel-cache"):
            raise CacheContractError(f"{path}: X-Vercel-Cache is required")

        conditional = fetch(path, etag)
        if conditional.status != 304:
            raise CacheContractError(
                f"{path}: If-None-Match expected 304, received {conditional.status}"
            )
        if conditional.body:
            raise CacheContractError(f"{path}: 304 response must not include a body")

        repeated = fetch(path, None)
        repeated_headers = _headers(repeated.headers)
        digest = hashlib.sha256(initial.body).hexdigest()
        if repeated.status != 200:
            raise CacheContractError(
                f"{path}: repeated request expected 200, received {repeated.status}"
            )
        if hashlib.sha256(repeated.body).hexdigest() != digest:
            raise CacheContractError(f"{path}: body changed during one probe")
        if repeated_headers.get("etag") != etag:
            raise CacheContractError(f"{path}: ETag changed during one probe")
        if require_vercel and not repeated_headers.get("x-vercel-cache"):
            raise CacheContractError(
                f"{path}: repeated response requires X-Vercel-Cache"
            )

        result = {
            "status": 200,
            "bytes": len(initial.body),
            "sha256": digest,
            "etag": etag,
            "cache_control": headers["cache-control"],
            "conditional_status": 304,
            "repeated_status": 200,
        }
        if headers.get("x-vercel-cache"):
            result["x_vercel_cache"] = headers["x-vercel-cache"]
        if repeated_headers.get("x-vercel-cache"):
            result["repeated_x_vercel_cache"] = repeated_headers["x-vercel-cache"]
        json_metadata = _verify_json(path, initial.body)
        if json_metadata is not None:
            payload, result["json_sha256"] = json_metadata
            result["record_count"] = len(payload)
            if path == "/companies.json":
                absent_site_ids = sorted(expected_absent_site_ids or ())
                absent_names = sorted(expected_absent_names or ())
                present_site_ids = {
                    item.get("site_id") for item in payload if isinstance(item, dict)
                }
                present_names = {
                    item.get("name") for item in payload if isinstance(item, dict)
                }
                unexpected_site_ids = sorted(set(absent_site_ids) & present_site_ids)
                unexpected_names = sorted(set(absent_names) & present_names)
                if unexpected_site_ids or unexpected_names:
                    raise CacheContractError(
                        "/companies.json: records expected absent are still deployed: "
                        f"site_ids={unexpected_site_ids}, names={unexpected_names}"
                    )
                if absent_site_ids:
                    result["verified_absent_site_ids"] = absent_site_ids
                if absent_names:
                    result["verified_absent_names"] = absent_names
        results[path] = result
    return results


def _resources(report: dict) -> dict:
    if not isinstance(report, dict) or report.get("schema_version") != 1:
        raise CacheContractError("report must use schema_version 1")
    resources = report.get("resources")
    if not isinstance(resources, dict) or set(resources) != set(DEFAULT_PATHS):
        raise CacheContractError(
            f"report resources must be exactly {sorted(DEFAULT_PATHS)}"
        )
    for path, evidence in resources.items():
        if not isinstance(evidence, dict):
            raise CacheContractError(f"{path}: report evidence must be an object")
        digest = evidence.get("sha256")
        etag = evidence.get("etag")
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise CacheContractError(f"{path}: report sha256 is invalid")
        if not isinstance(etag, str) or not etag.strip():
            raise CacheContractError(f"{path}: report ETag is missing")
        if (
            evidence.get("status") != 200
            or evidence.get("conditional_status") != 304
            or evidence.get("repeated_status") != 200
        ):
            raise CacheContractError(f"{path}: report status evidence is invalid")
        if _cache_directives(evidence.get("cache_control", "")) != REQUIRED_CACHE_DIRECTIVES:
            raise CacheContractError(f"{path}: report cache policy is invalid")
        if path.endswith(".json"):
            json_digest = evidence.get("json_sha256")
            record_count = evidence.get("record_count")
            if (
                not isinstance(json_digest, str)
                or len(json_digest) != 64
                or any(character not in "0123456789abcdef" for character in json_digest)
                or not isinstance(record_count, int)
                or isinstance(record_count, bool)
                or record_count < 0
            ):
                raise CacheContractError(f"{path}: report JSON evidence is invalid")
    return resources


def compare_revisions(
    previous: dict,
    current: dict,
    *, expected_changed: set[str] | None = None,
) -> dict:
    """Require content and ETag transitions to agree across two deployments."""
    before = _resources(previous)
    after = _resources(current)
    if set(before) != set(after):
        raise CacheContractError("resource paths changed between reports")
    changed = []
    for path in sorted(before):
        body_changed = before[path].get("sha256") != after[path].get("sha256")
        etag_changed = before[path].get("etag") != after[path].get("etag")
        if body_changed != etag_changed:
            detail = "ETag did not change" if body_changed else "ETag changed without content"
            raise CacheContractError(f"{path}: {detail}")
        if body_changed:
            changed.append(path)
    expected = sorted(expected_changed or ())
    if expected_changed is not None and changed != expected:
        raise CacheContractError(
            f"changed resources {changed} do not match expected {expected}"
        )
    return {"changed": changed, "unchanged": sorted(set(before) - set(changed))}


def verify_rollback(baseline: dict, current: dict) -> dict:
    """Require a rollback to restore every baseline body digest and ETag."""
    before = _resources(baseline)
    after = _resources(current)
    if set(before) != set(after):
        raise CacheContractError("rollback resource paths differ from baseline")
    mismatches = [
        path for path in sorted(before)
        if before[path].get("sha256") != after[path].get("sha256")
        or before[path].get("etag") != after[path].get("etag")
    ]
    if mismatches:
        raise CacheContractError(f"rollback does not match baseline: {mismatches}")
    return {"matches": True, "resources": sorted(before)}


def verify_local_data(report: dict, root: Path) -> dict:
    """Require deployed JSON to equal the reviewed repository data semantically."""
    resources = _resources(report)
    paths = ("/companies.json", "/ticker.json")
    mismatches = []
    for resource_path in paths:
        local_path = root / resource_path.lstrip("/")
        try:
            payload = json.loads(local_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CacheContractError(
                f"cannot read approved local data: {local_path}"
            ) from exc
        live_digest = resources.get(resource_path, {}).get("json_sha256")
        if live_digest != _json_digest(payload):
            mismatches.append(resource_path)
    if mismatches:
        raise CacheContractError(
            f"deployed JSON does not match approved local data: {mismatches}"
        )
    return {"matches": True, "resources": list(paths)}


def _base_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise argparse.ArgumentTypeError("base URL must be an HTTP(S) origin without credentials")
    return value.rstrip("/")


def _url_fetcher(base_url: str, timeout: float):
    def fetch(path: str, if_none_match: str | None = None) -> CacheResponse:
        url = urljoin(f"{base_url}/", path.lstrip("/"))
        headers = {
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.1",
            "Accept-Encoding": "identity",
            "User-Agent": "PeruGrid-Cache-Contract/1",
        }
        if if_none_match:
            headers["If-None-Match"] = if_none_match
        try:
            with urlopen(Request(url, headers=headers), timeout=timeout) as response:
                body = response.read(MAX_RESPONSE_BYTES + 1)
                if response.geturl() != url:
                    raise CacheContractError(
                        f"{path}: redirected to a different cache resource"
                    )
                return CacheResponse(
                    response.status, _headers(response.headers), body, response.geturl()
                )
        except HTTPError as exc:
            body = exc.read(MAX_RESPONSE_BYTES + 1)
            if exc.geturl() != url:
                raise CacheContractError(
                    f"{path}: redirected to a different cache resource"
                )
            return CacheResponse(exc.code, _headers(exc.headers), body, exc.geturl())
    return fetch


def _deployment(value: str) -> str:
    if re.fullmatch(r"dpl_[A-Za-z0-9]+", value):
        return value
    parsed = urlsplit(value)
    if (
        parsed.scheme == "https"
        and parsed.hostname
        and parsed.hostname.endswith(".vercel.app")
        and parsed.username is None
        and parsed.password is None
        and parsed.path in {"", "/"}
        and not parsed.query
        and not parsed.fragment
    ):
        return value.rstrip("/")
    raise argparse.ArgumentTypeError(
        "Vercel deployment must be a dpl_ ID or a vercel.app origin"
    )


def _parse_curl_headers(path: str, raw: bytes) -> tuple[int, dict[str, str]]:
    blocks = raw.replace(b"\r\n", b"\n").strip().split(b"\n\n")
    http_blocks = [block for block in blocks if block.startswith(b"HTTP/")]
    if not http_blocks:
        raise CacheContractError(f"{path}: vercel curl returned no HTTP headers")
    lines = http_blocks[-1].decode("iso-8859-1").splitlines()
    status_parts = lines[0].split()
    if len(status_parts) < 2 or not status_parts[1].isdigit():
        raise CacheContractError(f"{path}: vercel curl returned an invalid status")
    headers = {}
    for line in lines[1:]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip().casefold()] = value.strip()
    return int(status_parts[1]), headers


def _vercel_fetcher(deployment: str, timeout: float):
    executable = shutil.which("vercel")
    if not executable:
        raise CacheContractError("vercel CLI is required for a protected deployment")
    if not (Path.cwd() / ".vercel" / "project.json").is_file():
        raise CacheContractError(
            "protected preview requires an explicitly linked Vercel checkout"
        )

    def fetch(path: str, if_none_match: str | None = None) -> CacheResponse:
        with tempfile.TemporaryDirectory() as directory:
            headers_path = Path(directory) / "headers.txt"
            body_path = Path(directory) / "body.bin"
            command = [
                executable,
                "curl",
                path,
                "--deployment",
                deployment,
                "--",
                "--silent",
                "--show-error",
                "--max-time",
                str(timeout),
                "--max-filesize",
                str(MAX_RESPONSE_BYTES),
                "--dump-header",
                str(headers_path),
                "--output",
                str(body_path),
            ]
            if if_none_match:
                command.extend(("--header", f"If-None-Match: {if_none_match}"))
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    timeout=timeout + 30,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise CacheContractError(f"{path}: vercel curl timed out") from exc
            if completed.returncode != 0:
                raise CacheContractError(
                    f"{path}: vercel curl failed with exit {completed.returncode}"
                )
            try:
                raw_headers = headers_path.read_bytes()
                body = body_path.read_bytes() if body_path.exists() else b""
            except OSError as exc:
                raise CacheContractError(
                    f"{path}: cannot read vercel curl response"
                ) from exc
            status, headers = _parse_curl_headers(path, raw_headers)
            return CacheResponse(status, headers, body)

    return fetch


def _verify_vercel_target(
    deployment: str | None,
    base_url: str,
    deployment_id: str | None,
) -> None:
    if not deployment:
        return
    if deployment.startswith("https://") and deployment != base_url:
        raise CacheContractError(
            "Vercel deployment URL must equal --base-url"
        )
    if deployment.startswith("dpl_") and deployment_id and deployment != deployment_id:
        raise CacheContractError(
            "Vercel deployment ID must equal --deployment-id"
        )


def _load_report(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CacheContractError(f"cannot read report: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", type=_base_url, default=DEFAULT_BASE_URL)
    parser.add_argument(
        "--vercel-deployment",
        type=_deployment,
        help="use authenticated vercel curl for a protected preview",
    )
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare")
    parser.add_argument("--expect-changed", action="append")
    parser.add_argument("--expect-rollback")
    parser.add_argument(
        "--expect-local-data",
        action="store_true",
        help="require deployed JSON to match companies.json and ticker.json",
    )
    parser.add_argument(
        "--require-vercel",
        action="store_true",
        help="require X-Vercel-Cache on initial and repeated responses",
    )
    parser.add_argument(
        "--expect-absent-site-id",
        action="append",
        help="site_id that must be absent from deployed companies.json",
    )
    parser.add_argument(
        "--expect-absent-name",
        action="append",
        help="exact company name that must be absent from deployed companies.json",
    )
    parser.add_argument(
        "--deployment-id",
        help="immutable deployment identifier recorded in the report",
    )
    parser.add_argument(
        "--git-commit",
        help="deployed Git commit recorded in the report",
    )
    args = parser.parse_args(argv)
    if not 1 <= args.timeout <= 60:
        parser.error("--timeout must be between 1 and 60 seconds")

    try:
        _verify_vercel_target(
            args.vercel_deployment, args.base_url, args.deployment_id
        )
        report = {
            "schema_version": 1,
            "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "base_url": args.base_url,
            "resources": probe_resources(
                (
                    _vercel_fetcher(args.vercel_deployment, args.timeout)
                    if args.vercel_deployment
                    else _url_fetcher(args.base_url, args.timeout)
                ),
                expected_absent_site_ids=set(args.expect_absent_site_id or ()),
                expected_absent_names=set(args.expect_absent_name or ()),
                require_vercel=args.require_vercel,
            ),
        }
        if args.deployment_id:
            report["deployment_id"] = args.deployment_id
        if args.vercel_deployment:
            report["vercel_deployment"] = args.vercel_deployment
        if args.git_commit:
            report["git_commit"] = args.git_commit
        if args.expect_local_data:
            report["local_data"] = verify_local_data(report, Path.cwd())
        if args.compare:
            report["comparison"] = compare_revisions(
                _load_report(args.compare), report,
                expected_changed=(
                    set(args.expect_changed) if args.expect_changed is not None else None
                ),
            )
        elif args.expect_changed:
            raise CacheContractError("--expect-changed requires --compare")
        if args.expect_rollback:
            report["rollback"] = verify_rollback(
                _load_report(args.expect_rollback), report
            )
        serialized = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.write_text(serialized, encoding="utf-8", newline="\n")
        else:
            print(serialized, end="")
    except (CacheContractError, OSError, URLError) as exc:
        print(f"cache contract FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
