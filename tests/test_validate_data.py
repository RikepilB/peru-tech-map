"""Contrato público: ejecutar con python -m unittest discover -s tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_data import load_json, safe_domain_url, safe_logo_path, validate_companies, validate_ticker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "tests/fixtures/security.json").read_text(encoding="utf-8"))


class DataValidationTests(unittest.TestCase):
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
        for field in ("name", "city", "lat", "lng", "funding"):
            row = copy.deepcopy(FIXTURE["company"])
            del row[field]
            self.assertTrue(validate_companies([row]))

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
