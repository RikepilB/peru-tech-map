import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_cache import (
    CacheContractError,
    CacheResponse,
    _parse_curl_headers,
    _verify_vercel_target,
    compare_revisions,
    probe_resources,
    verify_local_data,
    verify_rollback,
)


ROOT = Path(__file__).parents[1]
MUTABLE_PATHS = ("/", "/index.html", "/companies.json", "/ticker.json")


class CacheContractTests(unittest.TestCase):
    def test_vercel_policy_revalidates_every_mutable_resource(self):
        config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        policies = {
            item["source"]: {
                header["key"].casefold(): header["value"]
                for header in item["headers"]
            }
            for item in config["headers"]
        }

        self.assertEqual(set(policies), set(MUTABLE_PATHS))
        for path in MUTABLE_PATHS:
            self.assertEqual(
                policies[path]["cache-control"],
                "public, max-age=0, must-revalidate",
            )

    def test_probe_requires_revalidation_and_never_keeps_response_bodies(self):
        bodies = {
            "/": b"<html>PeruGrid</html>",
            "/index.html": b"<html>PeruGrid</html>",
            "/companies.json": b'[{"site_id":"a"}]',
            "/ticker.json": b'[{"label":"TEST","text":"Cache"}]',
        }
        etags = {
            path: f'"{hashlib.sha256(body).hexdigest()}"'
            for path, body in bodies.items()
        }

        def fetch(path, if_none_match=None):
            headers = {
                "etag": etags[path],
                "cache-control": "public, max-age=0, must-revalidate",
                "x-vercel-cache": "HIT",
            }
            if if_none_match == etags[path]:
                return CacheResponse(304, headers, b"")
            return CacheResponse(200, headers, bodies[path])

        report = probe_resources(
            fetch,
            expected_absent_site_ids={"retired-site"},
            expected_absent_names={"Retired Space"},
        )

        self.assertEqual(set(report), set(bodies))
        for path, result in report.items():
            self.assertEqual(result["status"], 200)
            self.assertEqual(result["conditional_status"], 304)
            self.assertEqual(
                result["sha256"], hashlib.sha256(bodies[path]).hexdigest()
            )
            self.assertNotIn("body", result)
            self.assertEqual(result["repeated_x_vercel_cache"], "HIT")
        self.assertIn("json_sha256", report["/companies.json"])
        self.assertNotIn("json_sha256", report["/"])
        self.assertEqual(
            report["/companies.json"]["verified_absent_site_ids"],
            ["retired-site"],
        )
        self.assertEqual(
            report["/companies.json"]["verified_absent_names"],
            ["Retired Space"],
        )

        with self.assertRaisesRegex(CacheContractError, "still deployed"):
            probe_resources(fetch, expected_absent_site_ids={"a"})

        with self.assertRaisesRegex(CacheContractError, "exactly"):
            def conflicting_fetch(path, if_none_match=None):
                response = fetch(path, if_none_match)
                return CacheResponse(
                    response.status,
                    {**response.headers, "cache-control": (
                        "public, max-age=0, must-revalidate, no-store"
                    )},
                    response.body,
                )

            probe_resources(conflicting_fetch)

        with self.assertRaisesRegex(CacheContractError, "X-Vercel-Cache"):
            def non_vercel_fetch(path, if_none_match=None):
                response = fetch(path, if_none_match)
                headers = {
                    key: value
                    for key, value in response.headers.items()
                    if key.casefold() != "x-vercel-cache"
                }
                return CacheResponse(response.status, headers, response.body)

            probe_resources(non_vercel_fetch, require_vercel=True)

    def test_live_json_must_match_approved_local_data_semantically(self):
        companies = [{"name": "Keep", "city": "lima"}]
        ticker = []
        report = _report(
            json.dumps(companies, separators=(",", ":")).encode("utf-8"),
            '"companies-v1"',
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "companies.json").write_text(
                json.dumps(companies, indent=4), encoding="utf-8"
            )
            (root / "ticker.json").write_text(
                json.dumps(ticker, separators=(",", ":")), encoding="utf-8"
            )

            self.assertEqual(
                verify_local_data(report, root),
                {"matches": True, "resources": ["/companies.json", "/ticker.json"]},
            )

            (root / "companies.json").write_text(
                json.dumps(companies + [{"name": "Retired", "city": "lima"}]),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CacheContractError, "approved local data"):
                verify_local_data(report, root)

    def test_revision_comparison_covers_publish_removal_and_rollback(self):
        baseline = _report(b'[{"id":"keep"},{"id":"retire"}]', '"companies-v1"')
        published = _report(b'[{"id":"keep"}]', '"companies-v2"')
        rolled_back = _report(
            b'[{"id":"keep"},{"id":"retire"}]', '"companies-v1"'
        )

        transition = compare_revisions(
            baseline, published, expected_changed={"/companies.json"}
        )

        self.assertEqual(transition["changed"], ["/companies.json"])
        self.assertTrue(verify_rollback(baseline, rolled_back)["matches"])

    def test_revision_comparison_rejects_changed_body_with_reused_etag(self):
        baseline = _report(b'[{"id":"old"}]', '"companies-v1"')
        broken = _report(b'[{"id":"new"}]', '"companies-v1"')

        with self.assertRaisesRegex(CacheContractError, "ETag did not change"):
            compare_revisions(
                baseline, broken, expected_changed={"/companies.json"}
            )

    def test_revision_comparison_rejects_malformed_evidence(self):
        malformed = _report(b'[{"id":"old"}]', '"companies-v1"')
        del malformed["resources"]["/companies.json"]["sha256"]

        with self.assertRaisesRegex(CacheContractError, "sha256 is invalid"):
            compare_revisions(malformed, malformed)
        with self.assertRaisesRegex(CacheContractError, "sha256 is invalid"):
            verify_rollback(malformed, malformed)

        missing_replay = _report(b'[{"id":"old"}]', '"companies-v1"')
        del missing_replay["resources"]["/companies.json"]["repeated_status"]
        with self.assertRaisesRegex(CacheContractError, "status evidence is invalid"):
            compare_revisions(missing_replay, missing_replay)

    def test_vercel_curl_header_parser_uses_final_http_block(self):
        status, headers = _parse_curl_headers(
            "/companies.json",
            b"HTTP/1.1 100 Continue\r\n\r\n"
            b"HTTP/2 304\r\nETag: \"dataset\"\r\n"
            b"X-Vercel-Cache: HIT\r\n\r\n",
        )

        self.assertEqual(status, 304)
        self.assertEqual(headers["etag"], '"dataset"')
        self.assertEqual(headers["x-vercel-cache"], "HIT")

    def test_vercel_target_metadata_cannot_name_another_deployment(self):
        with self.assertRaisesRegex(CacheContractError, "must equal --base-url"):
            _verify_vercel_target(
                "https://preview-a.vercel.app",
                "https://preview-b.vercel.app",
                None,
            )
        with self.assertRaisesRegex(CacheContractError, "must equal --deployment-id"):
            _verify_vercel_target(
                "dpl_AAAA",
                "https://preview-a.vercel.app",
                "dpl_BBBB",
            )

        _verify_vercel_target(
            "dpl_AAAA",
            "https://preview-a.vercel.app",
            "dpl_AAAA",
        )


def _json_digest(value):
    canonical = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _report(company_body: bytes, company_etag: str):
    company_payload = json.loads(company_body)
    common = {
        "status": 200,
        "conditional_status": 304,
        "repeated_status": 200,
        "cache_control": "public, max-age=0, must-revalidate",
    }
    return {
        "schema_version": 1,
        "resources": {
            "/": {
                **common,
                "sha256": hashlib.sha256(b"html").hexdigest(),
                "etag": '"html"',
            },
            "/index.html": {
                **common,
                "sha256": hashlib.sha256(b"html").hexdigest(),
                "etag": '"html"',
            },
            "/companies.json": {
                **common,
                "sha256": hashlib.sha256(company_body).hexdigest(),
                "etag": company_etag,
                "json_sha256": _json_digest(company_payload),
                "record_count": len(company_payload),
            },
            "/ticker.json": {
                **common,
                "sha256": hashlib.sha256(b"[]").hexdigest(),
                "etag": '"ticker"',
                "json_sha256": _json_digest([]),
                "record_count": 0,
            },
        }
    }


if __name__ == "__main__":
    unittest.main()
