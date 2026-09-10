import unittest
from html.parser import HTMLParser
from pathlib import Path
import re

from scripts.validate_data import CATEGORIES, STARTUP_SUBCATEGORIES


ROOT = Path(__file__).resolve().parents[1]


class HeadLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current_select = None
        self.select_options = {}

    def handle_starttag(self, tag, attrs):
        if tag == "link":
            self.links.append(dict(attrs))
        attributes = dict(attrs)
        if tag == "select":
            self.current_select = attributes.get("id")
            if self.current_select:
                self.select_options[self.current_select] = []
        elif tag == "option" and self.current_select and attributes.get("value"):
            self.select_options[self.current_select].append(attributes["value"])

    def handle_endtag(self, tag):
        if tag == "select":
            self.current_select = None


class LaunchContractTests(unittest.TestCase):
    def test_canonical_url_matches_public_domain(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        parser = HeadLinkParser()
        parser.feed(html)

        canonical = [
            link.get("href")
            for link in parser.links
            if link.get("rel") == "canonical"
        ]

        self.assertEqual(canonical, ["https://perugrid.com/"])
        self.assertIn('<meta property="og:url" content="https://perugrid.com/" />', html)

    def test_robots_allows_the_public_page(self):
        directives = (ROOT / "robots.txt").read_text(encoding="utf-8").splitlines()

        self.assertEqual(directives, ["User-agent: *", "Allow: /"])

    def test_submission_surfaces_match_the_public_category_contract(self):
        parser = HeadLinkParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        issue_template = (ROOT / ".github/ISSUE_TEMPLATE/add_company.yml").read_text(
            encoding="utf-8"
        )
        category_section = issue_template.split("id: category", 1)[1].split(
            "- type:", 1
        )[0]
        issue_categories = set(
            re.findall(r"^\s{8}- (.+)$", category_section, flags=re.MULTILINE)
        )
        subcategory_section = issue_template.split("id: subcategory", 1)[1].split(
            "- type:", 1
        )[0]
        issue_subcategories = set(
            re.findall(r"^\s{8}- (.+)$", subcategory_section, flags=re.MULTILINE)
        )

        self.assertEqual(set(parser.select_options["catSelect"]), CATEGORIES)
        self.assertEqual(issue_categories, CATEGORIES)
        self.assertEqual(
            set(parser.select_options["subcategorySelect"]),
            STARTUP_SUBCATEGORIES,
        )
        self.assertEqual(issue_subcategories, STARTUP_SUBCATEGORIES)


if __name__ == "__main__":
    unittest.main()
