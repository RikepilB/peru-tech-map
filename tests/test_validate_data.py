"""Contrato público: ejecutar con python -m unittest discover -s tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_data import (
    CATEGORIES,
    STARTUP_SUBCATEGORIES,
    load_json,
    safe_domain_url,
    safe_logo_path,
    validate_companies,
    validate_ticker,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "tests/fixtures/security.json").read_text(encoding="utf-8"))


class DataValidationTests(unittest.TestCase):
    def test_current_dataset_has_complete_explicit_taxonomy(self):
        companies = load_json(ROOT / "companies.json")
        self.assertEqual(len(companies), 89)
        self.assertEqual(
            {category: sum(row["category"] == category for row in companies) for category in CATEGORIES},
            {
                "Startup": 37,
                "Incubator": 8,
                "Accelerator": 3,
                "VC": 4,
                "Nonprofit": 6,
                "Technology Consultancy": 12,
                "Coworking Space": 19,
            },
        )
        for row in companies:
            self.assertIn(row["category"], CATEGORIES)
            if "subcategory" in row:
                self.assertEqual(row["category"], "Startup")
                self.assertIn(row["subcategory"], STARTUP_SUBCATEGORIES)
            # Campo heredado conservado durante la migración expand/contract.
            self.assertIn("funding", row)
        by_name = {row["name"]: row["category"] for row in companies}
        self.assertEqual(
            {name: by_name[name] for name in (
                "PECAP", "Belatrix (Globant)", "Dentito", "Joinnus",
                "UTEC Ventures", "Wayra Perú", "LIQUID Venture Studio",
            )},
            {
                "PECAP": "Nonprofit",
                "Belatrix (Globant)": "Technology Consultancy",
                "Dentito": "Startup",
                "Joinnus": "Startup",
                "UTEC Ventures": "Accelerator",
                "Wayra Perú": "Accelerator",
                "LIQUID Venture Studio": "Accelerator",
            },
        )

    def test_data01_reconciles_verified_sites_without_generic_pins(self):
        companies = load_json(ROOT / "companies.json")
        by_name = {row["name"]: row for row in companies}

        for removed in ("WeWork San Isidro", "MindQube", "Talently", "uDocz"):
            self.assertNotIn(removed, by_name)

        expected_sites = {
            "WeWork Jorge Basadre 349": (-12.0948671, -77.0360040, "coworking"),
            "WeWork Real 2": (-12.0962186, -77.0368662, "coworking"),
            "Regus Real Ocho": (-12.0968638, -77.0378679, "coworking"),
            "Vallejo Librería-Café": (-12.1052878, -77.0388445, "cafe"),
            "La Bodega Verde": (-12.1482221, -77.0225903, "cafe"),
            "Sofá Café Barranco": (-12.1413883, -77.0231407, "cafe"),
            "Biblioteca Municipal de Barranco": (-12.1501191, -77.0214626, "library"),
            "Biblioteca Municipal de San Isidro": (-12.1015418, -77.0356762, "library"),
        }
        for name, (lat, lng, workspace_type) in expected_sites.items():
            with self.subTest(name=name):
                row = by_name[name]
                self.assertEqual((row["lat"], row["lng"]), (lat, lng))
                self.assertEqual(row["workspace_type"], workspace_type)
                self.assertTrue(row["site_id"])
                self.assertTrue(row["organization_id"])
                self.assertEqual(row["sources"][0]["provider"], "openstreetmap")
                self.assertEqual(row["sources"][0]["provenance_class"], "public")
                self.assertEqual(row["sources"][0]["use_classification"], "redistributable")
                self.assertIs(row["sources"][0]["export_eligible"], True)

        self.assertEqual(by_name["Sofá Café Barranco"]["address"], "Av. San Martín 480, Barranco, Lima")
        self.assertEqual(
            by_name["Biblioteca Municipal de Barranco"]["address"],
            "Av. San Martín s/n, Parque Municipal, Barranco, Lima",
        )

    def test_taxonomy_is_required_and_conditional(self):
        valid = copy.deepcopy(FIXTURE["company"])
        self.assertEqual(validate_companies([valid]), [])

        mutations = (
            ("missing category", lambda row: row.pop("category")),
            ("unknown category", lambda row: row.update(category="Fund")),
            ("unknown subcategory", lambda row: row.update(subcategory="Series B")),
            ("subcategory on non-startup", lambda row: row.update(category="VC")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                row = copy.deepcopy(valid)
                mutate(row)
                self.assertTrue(validate_companies([row]))

        for subcategory in STARTUP_SUBCATEGORIES:
            with self.subTest(subcategory=subcategory):
                row = dict(valid, subcategory=subcategory)
                self.assertEqual(validate_companies([row]), [])

        without_subcategory = copy.deepcopy(valid)
        without_subcategory.pop("subcategory")
        self.assertEqual(validate_companies([without_subcategory]), [])

    def test_current_datasets_pass_without_mutation(self):
        for name, validator in (("companies.json", validate_companies), ("ticker.json", validate_ticker)):
            data = load_json(ROOT / name)
            before = copy.deepcopy(data)
            self.assertEqual(validator(data), [])
            self.assertEqual(data, before)

    def test_text_is_data_not_a_reason_to_strip_content(self):
        self.assertEqual(validate_companies([FIXTURE["company"]]), [])
        self.assertEqual(validate_ticker(FIXTURE["ticker"]), [])

    def test_domain_and_logo_contract(self):
        for name in FIXTURE["valid_domains"]:
            self.assertEqual(safe_domain_url(name), "https://" + name)
        for name in FIXTURE["invalid_domains"]:
            with self.subTest(domain=name):
                self.assertIsNone(safe_domain_url(name))
        for name in FIXTURE["valid_logos"]:
            self.assertEqual(safe_logo_path(name), name)
        for name in FIXTURE["invalid_logos"]:
            with self.subTest(logo=name):
                self.assertIsNone(safe_logo_path(name))

    def test_rejects_invalid_roots_and_rows(self):
        for data in (None, {}, "data", 42, [None], [42], [[]]):
            for validate in (validate_companies, validate_ticker):
                with self.subTest(data=data, validator=validate.__name__):
                    self.assertTrue(validate(data))
        self.assertEqual(validate_companies([]), [])
        self.assertEqual(validate_ticker([]), [])

    def test_company_required_types_enums_and_coordinates(self):
        mutations = {
            "name": [None, "", 12, []], "city": ["bogota", None, []],
            "lat": [True, "-12.093", None, float("nan"), float("inf"), 10 ** 400, -99],
            "lng": [False, "-77.027", None, float("inf"), 0],
            "funding": [None, [], {}, {"type": []}, {"type": "Unknown"},
                        {"type": "Startup", "stage": "invented"},
                        {"type": "Coworking", "stage": "Seed"}],
            "category": [None, "", "Fund", "Consultancy", []],
            "subcategory": [None, "", "Revenue", "Series A", []],
            "domain": ["https://example.com", "example.com@evil.test", None],
            "logo": ["../image.png", "https://evil.test/a.png"],
            "operating_model": ["unknown", [], None], "logoDark": ["true", 1],
            "address": [42, []], "tag_es": [None, {}], "unexpected": [True],
        }
        for field, values in mutations.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    row = copy.deepcopy(FIXTURE["company"])
                    row[field] = value
                    self.assertTrue(validate_companies([row]))
        for field in ("name", "city", "lat", "lng", "category", "funding"):
            row = copy.deepcopy(FIXTURE["company"])
            del row[field]
            self.assertTrue(validate_companies([row]))

    def test_form_uses_only_public_taxonomy_values(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        category_block = html.split('<select name="Category"', 1)[1].split("</select>", 1)[0]
        stage_block = html.split('<select name="Subcategory"', 1)[1].split("</select>", 1)[0]
        for value in CATEGORIES:
            self.assertIn(f'value="{value}"', category_block)
        for legacy in ("Consultancy", "Coworking", "Fund"):
            self.assertNotIn(f'value="{legacy}"', category_block)
        for value in STARTUP_SUBCATEGORIES:
            self.assertIn(f'value="{value}"', stage_block)
        for legacy in ("Revenue", "Series A", "Series B", "Series C+", "Acquired", "Late Stage"):
            self.assertNotIn(f'value="{legacy}"', stage_block)

    def test_coordinate_boundaries_and_different_city(self):
        for city, lat, lng in (("lima", -12.35, -77.20), ("lima", -11.95, -76.90),
                               ("arequipa", -16.50, -71.60), ("arequipa", -16.30, -71.45)):
            row = dict(FIXTURE["company"], city=city, lat=lat, lng=lng)
            self.assertEqual(validate_companies([row]), [])
        self.assertTrue(validate_companies([dict(FIXTURE["company"], city="arequipa")]))

    def test_duplicate_identity_preserves_distinct_branches_and_colocation(self):
        row = dict(FIXTURE["company"], name="Café Uno")
        self.assertTrue(validate_companies([row, dict(row, name="  CAFÉ   UNO ")]))
        self.assertEqual(validate_companies([row, dict(row, lat=-12.10)]), [])
        self.assertEqual(validate_companies([row, dict(row, name="Otra empresa")]), [])

    def test_optional_scout_metadata_is_strict_and_site_ids_are_unique(self):
        package = load_json(ROOT / "tests/fixtures/scout_perugrid_v1.json")
        source = package["records"][0]["sources"][0]
        row = dict(
            FIXTURE["company"],
            category="Coworking Space",
            funding={"type": "Coworking"},
            site_id="site-fixture",
            organization_id="org-fixture",
            workspace_type="cafe",
            sources=[source],
        )
        row.pop("subcategory", None)
        self.assertEqual(validate_companies([row]), [])

        mutations = (
            lambda item: item.update(site_id=[]),
            lambda item: item.update(organization_id=True),
            lambda item: item.update(workspace_type="restaurant"),
            lambda item: item.update(sources=[]),
            lambda item: item["sources"][0].update(provider="Google Maps Platform"),
            lambda item: item["sources"][0].update(source_url="https://example.org/site?key=x"),
            lambda item: item["sources"][0].update(unexpected=True),
            lambda item: item["sources"].append(copy.deepcopy(item["sources"][0])),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                changed = copy.deepcopy(row)
                mutate(changed)
                self.assertTrue(validate_companies([changed]))
        second = dict(row, name="Otra", lat=-12.10)
        self.assertTrue(validate_companies([row, second]))

        for missing in ("site_id", "organization_id", "workspace_type", "sources"):
            with self.subTest(missing=missing):
                incomplete = copy.deepcopy(row)
                incomplete.pop(missing)
                self.assertTrue(validate_companies([incomplete]))

        canonical_duplicate = dict(row, site_id="SITE-FIXTURE", name="Otra", lat=-12.10)
        self.assertTrue(validate_companies([row, canonical_duplicate]))

        scout_mutations = (
            lambda item: item.update(name="Scout  place"),
            lambda item: item.update(address="Scout\nplace"),
            lambda item: item.pop("address"),
            lambda item: item.update(category="Startup"),
            lambda item: item.update(funding={"type": "Startup"}),
        )
        for mutate in scout_mutations:
            with self.subTest(scout_contract=mutate):
                changed = copy.deepcopy(row)
                mutate(changed)
                self.assertTrue(validate_companies([changed]))

    def test_invalid_ticker_and_duplicates(self):
        for row in ({}, {"label": 1, "text": "a"}, {"label": "x", "text": ""},
                    {"label": "x", "text": "a", "unknown": 1}):
            self.assertTrue(validate_ticker([row]))
        self.assertTrue(validate_ticker(FIXTURE["ticker"] * 2))

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_literals(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            for content in ('{"a":1,"a":2}', '[NaN]', '[Infinity]', '[1e999]', '{invalid'):
                path.write_text(content, encoding="utf-8")
                with self.subTest(content=content), self.assertRaises(ValueError):
                    load_json(path)

    def test_cli_failure_is_nonzero_and_does_not_rewrite_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "companies.json"
            path.write_text('[{"name":"incomplete"}]', encoding="utf-8")
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_data.py"),
                                     "--companies", str(path), "--ticker", str(ROOT / "ticker.json")],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("companies[0]", result.stderr)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
