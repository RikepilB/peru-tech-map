"""Pruebas DOM en Chromium del código real inline; MapLibre se dobla, sin red.

No son una prueba del renderer WebGL ni de los tiles de producción.
"""
import json
from pathlib import Path
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
FIXTURE = json.loads((ROOT / "tests/fixtures/security.json").read_text(encoding="utf-8"))
# Ejecutar las funciones del producto, no copias de su lógica de renderizado.
RENDER = HTML.split("// ---------- Companies", 1)[1].split("// ---------- Controls", 1)[0]
RENDER = RENDER[RENDER.index("const markers"):]
CONFIG = HTML.split("function bootApp() {", 1)[1].split("const map = new maplibregl.Map", 1)[0]
DICTIONARY = HTML.split("<script>", 1)[1].split("// Boot watchdog", 1)[0]
FORM_TAXONOMY = "const catSelect" + HTML.split("const catSelect", 1)[1].split("const modelSelect", 1)[0]
FILTER_CONTROLS = "// ---------- Controls" + HTML.split("// ---------- Controls", 1)[1].split(
    'document.getElementById("zin")', 1
)[0]
MOBILE_CONTROLS = "// ---------- Mobile sheet" + HTML.split("// ---------- Mobile sheet", 1)[1].split(
    "// ---------- Add-company modal", 1
)[0]
STYLES = HTML.split("<style>", 1)[1].split("</style>", 1)[0]
HARNESS = """
window.map = {on() {}, setMaxBounds() {}, setMinZoom() {}, flyTo() {}};
window.maplibregl = {
  Marker: class {
    constructor(opts) { this.element = opts.element; }
    setLngLat() { return this; }
    addTo() { document.querySelector('#map').append(this.element); return this; }
    remove() { this.element.remove(); }
  },
  Popup: class {
    constructor() { this.element = document.createElement('div'); this.element.className = 'test-popup'; }
    setLngLat() { return this; }
    setHTML(html) { this.element.innerHTML = html; return this; }
    addTo() { document.body.append(this.element); return this; }
    remove() { this.element.remove(); }
  }
};
window.__injected = 0;
"""
PAGE = f"""<style>{STYLES}</style>
<div id="map"></div><aside id="panel"><div id="handle"></div><div id="panelHead"><div id="coCount"></div>
<button class="barbtn active" data-city="lima">Lima</button><button class="barbtn" data-city="arequipa">Arequipa</button>
<button class="barbtn active" data-sort="default">Default</button><button class="barbtn" data-sort="alpha">A-Z</button>
<div class="filter-stack"><div class="filter-field"><label class="filter-label" for="viewCategory">What do you want to see?</label>
<select class="filter-select" id="viewCategory">
  <option value="">Companies</option><option value="Startup">Startup</option>
  <option value="Technology Consultancy">Technology Consultancy</option>
  <option value="Incubator">Incubator</option><option value="Accelerator">Accelerator</option>
  <option value="VC">VC</option><option value="Coworking Space">Coworking Space</option>
  <option value="Nonprofit">Nonprofit</option>
</select></div>
<div class="filter-field" id="viewStageField" hidden><label class="filter-label" for="viewStage">Startup stage</label>
  <select class="filter-select" id="viewStage"><option value="">All stages</option><option value="Pre-Seed">Pre-Seed</option>
  <option value="Seed">Seed</option><option value="Bootstrap">Bootstrap</option><option value="Series A+">Series A+</option></select>
</div>
<button class="filter-reset" id="clearViewFilters" hidden>Clear filters</button></div></div><div id="coList"></div></aside>
<button id="panelToggle"></button><div id="gridStatus"></div>
<div id="ticker"><div id="tickerTrack"></div></div>
<select id="catSelect"><option value="Startup">Startup</option><option value="VC">VC</option></select>
<div id="stageField"><select name="Subcategory"><option value=""></option><option value="Seed">Seed</option></select></div>"""


class RenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = sync_playwright().start()
        cls.browser = cls.driver.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.driver.stop()

    def setUp(self):
        self.context = self.browser.new_context(locale="es-PE")
        self.context.route("**/*", lambda route: route.fulfill(status=200, content_type="text/html", body=PAGE)
                           if route.request.url == "http://perugrid.test/" else route.abort())
        self.page = self.context.new_page()
        self.page.goto("http://perugrid.test/")
        self.page.add_script_tag(
            content=DICTIONARY + CONFIG + HARNESS + RENDER + FILTER_CONTROLS + MOBILE_CONTROLS + FORM_TAXONOMY
        )

    def tearDown(self):
        self.context.close()

    def render(self, company):
        self.page.evaluate("c => { COMPANIES = [c]; buildMarkers(); buildSidebar(); selectCompany(0, false); }", company)

    def assert_no_injection(self):
        self.assertEqual(self.page.evaluate("window.__injected"), 0)
        self.assertEqual(self.page.locator("[onerror], [onload], [onclick], svg").count(), 0)

    def test_malicious_text_renders_literally_in_list_popup_and_ticker(self):
        self.render(FIXTURE["company"])
        self.assertEqual(self.page.locator(".co .name").text_content(), FIXTURE["company"]["name"])
        self.assertEqual(self.page.locator(".pname").text_content(), FIXTURE["company"]["name"])
        self.assertEqual(self.page.locator(".ptag").text_content(), FIXTURE["company"]["tag_es"])
        self.assertEqual(self.page.locator(".addr").text_content(), FIXTURE["company"]["address"])
        self.page.evaluate("items => { window.fetch = async () => ({ok:true, json:async () => items}); }", FIXTURE["ticker"])
        self.page.evaluate("loadTicker()")
        self.assertEqual(self.page.locator(".ti-label").first.text_content(), FIXTURE["ticker"][0]["label"])
        self.assertIn(FIXTURE["ticker"][0]["text"], self.page.locator("#tickerTrack").text_content())
        self.assert_no_injection()

    def test_untrusted_funding_and_logo_attributes_cannot_create_markup(self):
        company = dict(FIXTURE["company"], logo='assets/logos/a.png" onerror="window.__injected=1',
                       domain='example.com" onclick="window.__injected=1',
                       category='<img src=x onerror=window.__injected=1>',
                       subcategory='<svg onload=window.__injected=1>',
                       funding={"type": '<img src=x onerror=window.__injected=1>',
                                "stage": '<svg onload=window.__injected=1>'})
        self.render(company)
        self.assertEqual(self.page.locator(".chip").first.text_content(), company["category"])
        self.assertEqual(self.page.locator(".site, .co img, .co-marker img").count(), 0)
        self.assert_no_injection()

    def test_url_rules_match_validator_vectors(self):
        for kind in ("domains", "logos"):
            expression = "safeDomainUrl(value)" if kind == "domains" else "safeLogoPath(value)"
            for value in FIXTURE["valid_" + kind]:
                with self.subTest(value=value):
                    self.assertTrue(self.page.evaluate("value => " + expression, value))
            for value in FIXTURE["invalid_" + kind]:
                with self.subTest(value=value):
                    self.assertIsNone(self.page.evaluate("value => " + expression, value))

    def test_current_data_city_filters_language_and_links(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        expected = [c for c in companies if c["city"] == "lima" and c["category"] in ("Startup", "Technology Consultancy")]
        self.assertEqual(self.page.locator(".co").count(), len(expected))
        self.page.locator(".co").first.click()
        self.assertEqual(self.page.locator(".ptag").text_content(), expected[0]["tag_es"])
        self.page.evaluate("localStorage.setItem('pg_lang', 'en'); window.__pgRefreshPopup()")
        self.assertEqual(self.page.locator(".ptag").text_content(), expected[0]["tag"])
        self.page.locator("#viewCategory").select_option("Coworking Space")
        self.page.evaluate("applyCity('arequipa')")
        expected = [c for c in companies if c["city"] == "arequipa" and c["category"] == "Coworking Space"]
        self.assertEqual(self.page.locator(".co").count(), len(expected))
        self.assertEqual(self.page.locator(".co-marker").count(), len(expected))
        self.assertEqual(self.page.locator(".test-popup").count(), 0)
        self.assert_no_injection()

    def test_new_taxonomy_is_preferred_and_legacy_funding_falls_back(self):
        modern = dict(FIXTURE["company"], category="Startup", subcategory="Pre-Seed",
                      funding={"type": "Acquired"})
        self.render(modern)
        self.assertEqual(self.page.locator(".co .tag").text_content(), "Pre-Seed")
        self.assertEqual(self.page.locator(".test-popup .chip").all_text_contents(), ["Startup", "Pre-Seed"])

        modern_without_stage = dict(modern, funding={"type": "Startup", "stage": "Revenue"})
        modern_without_stage.pop("subcategory")
        self.render(modern_without_stage)
        self.assertEqual(self.page.locator(".test-popup .chip").all_text_contents(), ["Startup"])

        legacy = dict(FIXTURE["company"])
        legacy.pop("category")
        legacy.pop("subcategory")
        self.render(legacy)
        self.assertEqual(self.page.locator(".co .tag").text_content(), "Seed")
        self.assertEqual(self.page.locator(".test-popup .chip").all_text_contents(), ["Startup", "Seed"])

    def test_hidden_subcategory_is_cleared_for_non_startup(self):
        subcategory = self.page.locator('[name="Subcategory"]')
        subcategory.select_option("Seed")
        self.page.locator("#catSelect").select_option("VC")
        self.assertEqual(subcategory.input_value(), "")
        self.assertEqual(self.page.locator("#stageField").evaluate("el => el.style.display"), "none")

    def test_category_select_exposes_all_public_views_and_preserves_city(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)

        category_select = self.page.locator("#viewCategory")
        self.assertEqual(category_select.locator("option").count(), 8)
        self.assertEqual(category_select.locator("option").evaluate_all("options => options.map(option => option.value)"), [
            "", "Startup", "Technology Consultancy", "Incubator", "Accelerator", "VC",
            "Coworking Space", "Nonprofit",
        ])
        for category in ("Startup", "Technology Consultancy", "Incubator", "Accelerator", "VC", "Coworking Space", "Nonprofit"):
            with self.subTest(category=category):
                category_select.select_option(category)
                expected = [c for c in companies if c["city"] == "lima" and c["category"] == category]
                self.assertEqual(self.page.locator(".co").count(), len(expected))
                self.assertEqual(category_select.input_value(), category)
                self.assertEqual(self.page.locator('[data-city="lima"]').get_attribute("class"), "barbtn active")

        self.page.evaluate("applyCity('arequipa')")
        self.assertEqual(self.page.locator(".co").count(), 0)
        self.assertEqual(self.page.locator(".panel-empty").count(), 1)

    def test_startup_stage_filter_and_clear_return_to_default_feed(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        default_count = len([
            c for c in companies
            if c["city"] == "lima" and c["category"] in ("Startup", "Technology Consultancy")
        ])

        category = self.page.locator("#viewCategory")
        stage = self.page.locator("#viewStage")
        category.select_option("Startup")
        self.assertFalse(self.page.locator("#viewStageField").is_hidden())
        stage.select_option("Seed")
        expected_seed = [
            c for c in companies
            if c["city"] == "lima" and c["category"] == "Startup" and c.get("subcategory") == "Seed"
        ]
        self.assertEqual(self.page.locator(".co").count(), len(expected_seed))
        self.assertEqual(self.page.locator(".co .tag").first.text_content(), "Seed")
        self.assertEqual(stage.input_value(), "Seed")

        stage.select_option("")
        expected_startups = len([c for c in companies if c["city"] == "lima" and c["category"] == "Startup"])
        self.assertEqual(self.page.locator(".co").count(), expected_startups)

        stage.select_option("Bootstrap")
        self.assertEqual(self.page.locator(".co").count(), 0)
        self.assertEqual(self.page.locator(".co-marker").count(), 0)
        self.assertEqual(self.page.locator(".panel-empty").text_content(), "No hay lugares que coincidan con estos filtros.")

        self.page.locator("#clearViewFilters").click()
        self.assertEqual(category.input_value(), "")
        self.assertTrue(self.page.locator("#viewStageField").is_hidden())
        self.assertTrue(self.page.locator("#clearViewFilters").is_hidden())
        self.assertEqual(self.page.locator(".co").count(), default_count)

    def test_filter_labels_have_english_and_spanish_copy(self):
        expected = {
            "en": ("What do you want to see?", "Companies", "Startup stage", "All stages", "Clear filters"),
            "es": ("¿Qué quieres ver?", "Empresas", "Etapa de startup", "Todas las etapas", "Limpiar filtros"),
        }
        for lang, labels in expected.items():
            with self.subTest(lang=lang):
                values = self.page.evaluate(
                    "lang => { localStorage.setItem('pg_lang', lang); return [t('filterCategory'), t('viewCompanies'), t('filterStage'), t('allStartupStages'), t('clearFilters')]; }",
                    lang,
                )
                self.assertEqual(tuple(values), labels)

    def test_desktop_filter_row_selection_and_popup_leave_panel_as_sidebar(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.set_viewport_size({"width": 1280, "height": 800})
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        self.page.locator("#viewCategory").select_option("VC")
        self.assertGreater(self.page.locator(".co").count(), 0)
        self.page.locator(".co").first.click()
        self.assertEqual(self.page.locator(".test-popup").count(), 1)
        self.page.locator("#panelHead").evaluate("el => el.click()")
        self.assertNotIn("expanded", self.page.locator("#panel").get_attribute("class") or "")

    def test_mobile_filter_row_selection_and_popup_collapse_expanded_sheet(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        self.page.locator("#panelHead").evaluate("el => el.click()")
        self.assertIn("expanded", self.page.locator("#panel").get_attribute("class") or "")

        self.page.locator("#viewCategory").select_option("Coworking Space")
        self.assertIn("expanded", self.page.locator("#panel").get_attribute("class") or "")
        self.assertGreater(self.page.locator(".co").count(), 0)
        self.page.locator(".co").first.click()
        self.assertEqual(self.page.locator(".test-popup").count(), 1)
        self.assertNotIn("expanded", self.page.locator("#panel").get_attribute("class") or "")

    def test_filter_hierarchy_keyboard_reset_and_mobile_targets(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        self.page.locator("#panelHead").evaluate("el => el.click()")
        self.page.locator('[data-city="arequipa"]').click()
        self.page.locator('[data-sort="alpha"]').click()

        category = self.page.locator("#viewCategory")
        stage = self.page.locator("#viewStage")
        clear = self.page.locator("#clearViewFilters")
        self.assertTrue(self.page.locator("#viewStageField").is_hidden())
        self.assertTrue(clear.is_hidden())
        self.assertGreaterEqual(category.bounding_box()["height"], 44)

        category.focus()
        category.press("ArrowDown")
        self.assertEqual(category.input_value(), "Startup")
        self.assertFalse(self.page.locator("#viewStageField").is_hidden())
        self.assertFalse(clear.is_hidden())
        self.assertGreaterEqual(stage.bounding_box()["height"], 44)

        stage.select_option("Seed")
        category.select_option("VC")
        self.assertEqual(stage.input_value(), "")
        self.assertTrue(self.page.locator("#viewStageField").is_hidden())

        clear.click()
        self.assertEqual(category.input_value(), "")
        self.assertEqual(self.page.locator('[data-city="arequipa"]').get_attribute("class"), "barbtn active")
        self.assertEqual(self.page.locator('[data-sort="alpha"]').get_attribute("class"), "barbtn active")

    def test_safe_legacy_path_and_logo_error_fallback(self):
        company = dict(FIXTURE["company"], name="O'Reilly & Co", domain=FIXTURE["valid_domains"][-1])
        self.render(company)
        self.assertEqual(self.page.locator(".site").get_attribute("href"), "https://" + company["domain"])
        self.page.locator(".co img").evaluate_all("imgs => imgs.forEach(img => img.dispatchEvent(new Event('error')))")
        self.assertEqual(self.page.locator(".co .initial").text_content(), "O")
        self.assert_no_injection()

    def test_failed_fetch_shows_error_state(self):
        self.page.evaluate("window.fetch = async () => ({ok:false, status:503})")
        self.page.evaluate("loadCompanies()")
        self.assertIn("FAIL", self.page.locator("#gridStatus").text_content())
        self.assertEqual(self.page.locator(".panel-err").count(), 1)
        self.assertEqual(self.page.locator(".co").count(), 0)


if __name__ == "__main__":
    unittest.main()
