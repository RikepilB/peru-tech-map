"""Contrato de integración INT-01 entre Coworking Scout y PeruGrid."""
import copy
import json
from pathlib import Path
from unittest import mock
import subprocess
import sys
import tempfile
import unittest

from scripts.import_scout import (
    ScoutImportError,
    import_package,
    plan_import,
    validate_scout_package,
)
from scripts.validate_data import load_json, validate_companies


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests/fixtures/scout_perugrid_v1.json"


def fixture_package() -> dict:
    return load_json(FIXTURE_PATH)


class ScoutPackageValidationTests(unittest.TestCase):
    def test_generated_synthetic_fixture_matches_strict_contract(self):
        package = fixture_package()
        self.assertEqual(validate_scout_package(package), [])
        self.assertEqual(package["records"][0]["city"], "Lima")
        self.assertNotIn("provider_ref", json.dumps(package))

    def test_rejects_unknown_version_roots_keys_and_record_keys(self):
        mutations = (
            lambda package: package.update(schema_version="perugrid.scout.v2"),
            lambda package: package.update(unexpected=True),
            lambda package: package.pop("records"),
            lambda package: package["records"][0].update(unexpected=True),
            lambda package: package["records"][0].pop("site_id"),
            lambda package: package["records"][0]["sources"][0].update(provider_ref="secret"),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                package = fixture_package()
                mutate(package)
                self.assertTrue(validate_scout_package(package))
        for root in (None, [], "package", 1):
            with self.subTest(root=root):
                self.assertTrue(validate_scout_package(root))

    def test_rejects_malformed_record_fields(self):
        cases = {
            "site_id": [None, "", 1, True],
            "organization_id": [None, "", [], True],
            "name": [None, "", 1],
            "address": [None, "", {}],
            "city": ["lima", "Cusco", None, []],
            "workspace_type": ["Coworking", "restaurant", None, []],
            "lat": [True, "-12.1", None, float("nan"), float("inf"), -11.80],
            "lng": [False, "-77.0", None, float("inf"), -77.40],
            "review_state": ["candidate", "", None, True],
            "export_eligible": [False, 1, "true", None],
            "sources": [[], None, {}, [None]],
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    package = fixture_package()
                    package["records"][0][field] = value
                    self.assertTrue(validate_scout_package(package))

    def test_rejects_unapproved_or_malformed_sources(self):
        cases = {
            "provider": ["Google", "google_maps", "Google Maps Platform", "", None],
            "source_url": [
                "http://example.org/site",
                "https://user:pass@example.org/site",
                "https://example.org/site?token=1",
                "https://example.org/site#private",
                "https://example.org:8443/site",
                "//example.org/site",
                "https://exa mple.org/site",
                None,
            ],
            "observed_at": ["2026-09-08", "2026-09-08T00:00:00", "not-a-date", None],
            "provenance_class": ["private", "unclassified", None, True],
            "use_classification": ["restricted", "unclassified", None, True],
            "export_eligible": [False, 1, "true", None],
        }
        for field, values in cases.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    package = fixture_package()
                    package["records"][0]["sources"][0][field] = value
                    self.assertTrue(validate_scout_package(package))

    def test_city_coordinate_pair_must_match_existing_bounds(self):
        package = fixture_package()
        package["records"][0].update(city="Arequipa", lat=-16.3989, lng=-71.5369)
        self.assertEqual(validate_scout_package(package), [])
        package["records"][0]["lat"] = -12.1191
        self.assertTrue(validate_scout_package(package))


class ScoutImportTests(unittest.TestCase):
    def setUp(self):
        self.companies = load_json(ROOT / "companies.json")
        self.package = fixture_package()

    def test_dry_run_maps_record_without_mutating_inputs(self):
        companies_before = copy.deepcopy(self.companies)
        package_before = copy.deepcopy(self.package)
        result = plan_import(self.package, self.companies)

        self.assertEqual((result.records, result.added, result.unchanged, result.total), (1, 1, 0, 91))
        self.assertEqual(self.companies, companies_before)
        self.assertEqual(self.package, package_before)
        self.assertEqual(result.companies[-1], {
            "name": "Nomad House Miraflores",
            "city": "lima",
            "address": "Avenida Larco 123, Miraflores",
            "lat": -12.1191,
            "lng": -77.0297,
            "category": "Coworking Space",
            "funding": {"type": "Coworking"},
            "site_id": "site-nomad-miraflores",
            "organization_id": "org-nomad-house",
            "workspace_type": "coworking",
            "sources": self.package["records"][0]["sources"],
        })
        self.assertEqual(validate_companies(result.companies), [])

    def test_all_public_workspace_types_map_to_coworking_category(self):
        for workspace_type in ("coworking", "cafe", "library"):
            with self.subTest(workspace_type=workspace_type):
                package = fixture_package()
                package["records"][0]["workspace_type"] = workspace_type
                result = plan_import(package, self.companies)
                self.assertEqual(result.companies[-1]["category"], "Coworking Space")
                self.assertEqual(result.companies[-1]["funding"], {"type": "Coworking"})
                self.assertEqual(result.companies[-1]["workspace_type"], workspace_type)

    def test_first_write_adds_and_second_write_is_an_idempotent_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            companies_path = Path(tmp) / "companies.json"
            companies_path.write_bytes((ROOT / "companies.json").read_bytes())

            first = import_package(FIXTURE_PATH, companies_path, write=True)
            self.assertEqual((first.added, first.unchanged, first.total), (1, 0, 91))
            first_bytes = companies_path.read_bytes()

            second = import_package(FIXTURE_PATH, companies_path, write=True)
            self.assertEqual((second.added, second.unchanged, second.total), (0, 1, 91))
            self.assertEqual(companies_path.read_bytes(), first_bytes)

    def test_default_dry_run_never_changes_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            companies_path = Path(tmp) / "companies.json"
            companies_path.write_bytes((ROOT / "companies.json").read_bytes())
            before = companies_path.read_bytes()

            result = import_package(FIXTURE_PATH, companies_path)

            self.assertEqual((result.added, result.total), (1, 91))
            self.assertEqual(companies_path.read_bytes(), before)

    def test_same_site_id_with_changed_payload_is_a_conflict(self):
        existing = plan_import(self.package, self.companies).companies
        changed = fixture_package()
        changed["records"][0]["address"] = "Otra dirección"
        with self.assertRaisesRegex(ScoutImportError, "conflicto"):
            plan_import(changed, existing)

    def test_normalized_name_city_coordinate_collision_is_a_conflict(self):
        colliding = copy.deepcopy(self.companies)
        colliding.append({
            "name": "  NOMAD   HOUSE MIRAFLORES ",
            "city": "lima",
            "lat": -12.1191,
            "lng": -77.0297,
            "category": "Coworking Space",
            "funding": {"type": "Coworking"},
        })
        with self.assertRaisesRegex(ScoutImportError, "colisión"):
            plan_import(self.package, colliding)

    def test_duplicate_site_id_inside_package_is_rejected(self):
        package = fixture_package()
        package["records"].append(copy.deepcopy(package["records"][0]))
        self.assertTrue(validate_scout_package(package))

    def test_invalid_prospective_dataset_cannot_be_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            companies_path = Path(tmp) / "companies.json"
            invalid = copy.deepcopy(self.companies)
            invalid[0]["category"] = "invented"
            companies_path.write_text(json.dumps(invalid), encoding="utf-8")
            before = companies_path.read_bytes()
            with self.assertRaises(ScoutImportError):
                import_package(FIXTURE_PATH, companies_path, write=True)
            self.assertEqual(companies_path.read_bytes(), before)

    def test_atomic_replace_failure_preserves_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            companies_path = Path(tmp) / "companies.json"
            companies_path.write_bytes((ROOT / "companies.json").read_bytes())
            before = companies_path.read_bytes()
            with mock.patch("scripts.import_scout.os.replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError):
                    import_package(FIXTURE_PATH, companies_path, write=True)
            self.assertEqual(companies_path.read_bytes(), before)
            self.assertEqual(list(Path(tmp).glob("*.tmp")), [])

    def test_cli_reports_deterministic_summary_and_contract_errors_are_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            companies_path = Path(tmp) / "companies.json"
            companies_path.write_bytes((ROOT / "companies.json").read_bytes())
            command = [sys.executable, str(ROOT / "scripts/import_scout.py"),
                       "--package", str(FIXTURE_PATH), "--companies", str(companies_path)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(),
                             "OK — mode=dry-run, records=1, added=1, unchanged=0, total=91")
            before = companies_path.read_bytes()

            invalid_path = Path(tmp) / "invalid.json"
            invalid = fixture_package()
            invalid["schema_version"] = "unknown"
            invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
            failed = subprocess.run([*command[:2], "--package", str(invalid_path),
                                     "--companies", str(companies_path), "--write"],
                                    capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("schema_version", failed.stderr)
            self.assertEqual(companies_path.read_bytes(), before)

    def test_current_dataset_and_bytes_remain_unchanged(self):
        before = (ROOT / "companies.json").read_bytes()
        self.assertEqual(validate_companies(self.companies), [])
        import_package(FIXTURE_PATH, ROOT / "companies.json")
        self.assertEqual((ROOT / "companies.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
