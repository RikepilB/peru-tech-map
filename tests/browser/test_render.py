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
<div id="map"></div><aside id="panel"><div id="handle"></div><div id="panelHead"><div id="coCount" aria-live="polite" aria-atomic="true"></div>
<button class="barbtn active" data-city="lima">Lima</button><button class="barbtn" data-city="arequipa">Arequipa</button>
<button class="barbtn active" data-sort="default">Default</button><button class="barbtn" data-sort="alpha">A-Z</button>
<div class="filter-stack">
<fieldset class="filter-field filter-group"><legend class="filter-label">Map mode</legend>
  <div class="mode-switch" id="viewModes">
    <label class="mode-choice"><input class="filter-input" type="radio" name="view-mode" value="ecosystem" data-view-mode="ecosystem" checked><span class="mode-choice-label">Ecosystem</span></label>
    <label class="mode-choice"><input class="filter-input" type="radio" name="view-mode" value="remote" data-view-mode="remote"><span class="mode-choice-label">Work remotely</span></label>
  </div>
</fieldset>
<fieldset class="filter-field filter-group" id="viewCategoryField"><legend class="filter-label">Organization types</legend>
<div class="filter-grid" id="viewCategories">
  <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-category="Startup" value="Startup" checked><span class="filter-choice-label">Startups</span></label>
  <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-category="Technology Consultancy" value="Technology Consultancy" checked><span class="filter-choice-label">Consultancies</span></label>
  <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-category="Coworking Space" value="Coworking Space"><span class="filter-choice-label">Coworking</span></label>
  <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-category="VC" value="VC"><span class="filter-choice-label">VC</span></label>
  <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-category="Incubator" value="Incubator"><span class="filter-choice-label">Incubators</span></label>
  <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-category="Accelerator" value="Accelerator"><span class="filter-choice-label">Accelerators</span></label>
  <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-category="Nonprofit" value="Nonprofit"><span class="filter-choice-label">Nonprofits</span></label>
</div></fieldset>
<fieldset class="filter-field filter-group" id="viewStageField"><legend class="filter-label">Startup stage</legend>
  <div class="filter-grid filter-stage-grid" id="viewStages">
    <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-stage="Pre-Seed" value="Pre-Seed"><span class="filter-choice-label">Pre-Seed</span></label>
    <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-stage="Seed" value="Seed"><span class="filter-choice-label">Seed</span></label>
    <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-stage="Bootstrap" value="Bootstrap"><span class="filter-choice-label">Bootstrap</span></label>
    <label class="filter-choice"><input class="filter-input" type="checkbox" data-view-stage="Series A+" value="Series A+"><span class="filter-choice-label">Series A+</span></label>
  </div>
</fieldset>
<fieldset class="filter-field filter-group" id="viewWorkspaceField" hidden><legend class="filter-label">Place types</legend>
  <div class="filter-grid filter-workspace-grid" id="viewWorkspaces">
    <label class="filter-choice"><input class="filter-input" type="checkbox" data-workspace-type="coworking" value="coworking" checked><span class="filter-choice-label">Coworking</span></label>
    <label class="filter-choice"><input class="filter-input" type="checkbox" data-workspace-type="cafe" value="cafe" checked><span class="filter-choice-label">Cafés</span></label>
    <label class="filter-choice"><input class="filter-input" type="checkbox" data-workspace-type="library" value="library" checked><span class="filter-choice-label">Libraries</span></label>
  </div>
  <p class="filter-note">Verified locations only.</p>
</fieldset>
<button class="filter-reset" id="clearViewFilters" hidden>Restore companies</button></div></div><div id="coList"></div></aside>
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

    def set_categories(self, *categories):
        wanted = set(categories)
        for option in self.page.locator("[data-view-category]").all():
            value = option.get_attribute("value")
            if value in wanted and not option.is_checked():
                option.locator("xpath=..").click()
            elif value not in wanted and option.is_checked():
                option.locator("xpath=..").click()

    def set_workspace_types(self, *workspace_types):
        wanted = set(workspace_types)
        for option in self.page.locator("[data-workspace-type]").all():
            value = option.get_attribute("value")
            if value in wanted and not option.is_checked():
                option.locator("xpath=..").click()
            elif value not in wanted and option.is_checked():
                option.locator("xpath=..").click()

    def set_mode(self, mode):
        option = self.page.locator(f'[data-view-mode="{mode}"]')
        if not option.is_checked():
            option.locator("xpath=..").click()

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
        self.set_categories("Coworking Space")
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

    def test_category_controls_combine_public_views_and_preserve_city(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)

        categories = self.page.locator("[data-view-category]")
        self.assertEqual(self.page.locator("#coCount").get_attribute("aria-live"), "polite")
        self.assertEqual(categories.count(), 7)
        self.assertEqual(categories.evaluate_all("options => options.map(option => option.value)"), [
            "Startup", "Technology Consultancy", "Coworking Space", "VC", "Incubator", "Accelerator", "Nonprofit",
        ])
        self.assertEqual(categories.evaluate_all("options => options.filter(option => option.checked).map(option => option.value)"), [
            "Startup", "Technology Consultancy",
        ])

        self.set_categories("Coworking Space", "VC")
        expected = [
            c for c in companies
            if c["city"] == "lima" and c["category"] in ("Coworking Space", "VC")
        ]
        self.assertEqual(self.page.locator(".co").count(), len(expected))
        self.assertEqual(self.page.locator(".co-marker").count(), len(expected))
        self.assertEqual(categories.evaluate_all("options => options.filter(option => option.checked).map(option => option.value)"), [
            "Coworking Space", "VC",
        ])
        self.assertEqual(self.page.locator('[data-city="lima"]').get_attribute("class"), "barbtn active")

        self.page.evaluate("applyCity('arequipa')")
        expected = [
            c for c in companies
            if c["city"] == "arequipa" and c["category"] in ("Coworking Space", "VC")
        ]
        self.assertEqual(self.page.locator(".co").count(), len(expected))

    def test_startup_stage_filter_and_clear_return_to_default_feed(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        default_count = len([
            c for c in companies
            if c["city"] == "lima" and c["category"] in ("Startup", "Technology Consultancy")
        ])

        self.set_categories("Startup", "VC")
        stage = self.page.locator('[data-view-stage="Seed"]')
        self.assertFalse(self.page.locator("#viewStageField").is_hidden())
        stage.locator("xpath=..").click()
        expected_seed = [
            c for c in companies
            if c["city"] == "lima" and (
                (c["category"] == "Startup" and c.get("subcategory") == "Seed") or c["category"] == "VC"
            )
        ]
        self.assertEqual(self.page.locator(".co").count(), len(expected_seed))
        self.assertTrue(stage.is_checked())

        self.page.locator('[data-view-stage="Pre-Seed"]').locator("xpath=..").click()
        expected_stages = [
            c for c in companies
            if c["city"] == "lima" and (
                (c["category"] == "Startup" and c.get("subcategory") in ("Seed", "Pre-Seed")) or c["category"] == "VC"
            )
        ]
        self.assertEqual(self.page.locator(".co").count(), len(expected_stages))

        self.page.locator('[data-view-category="Startup"]').locator("xpath=..").click()
        self.assertTrue(self.page.locator("#viewStageField").is_hidden())
        self.assertFalse(stage.is_checked())
        expected_vcs = len([c for c in companies if c["city"] == "lima" and c["category"] == "VC"])
        self.assertEqual(self.page.locator(".co").count(), expected_vcs)

        self.set_categories()
        self.assertEqual(self.page.locator(".co").count(), 0)
        self.assertEqual(self.page.locator(".co-marker").count(), 0)
        self.assertEqual(self.page.locator(".panel-empty").text_content(), "No hay lugares que coincidan con estos filtros.")

        self.page.locator("#clearViewFilters").click()
        self.assertEqual(self.page.locator("[data-view-category]").evaluate_all(
            "options => options.filter(option => option.checked).map(option => option.value)"
        ), ["Startup", "Technology Consultancy"])
        self.assertFalse(self.page.locator("#viewStageField").is_hidden())
        self.assertTrue(self.page.locator("#clearViewFilters").is_hidden())
        self.assertEqual(self.page.locator(".co").count(), default_count)

    def test_filter_labels_have_english_and_spanish_copy(self):
        expected = {
            "en": ("Organization types", "Startups", "Consultancies", "Startup stage · optional", "Restore companies"),
            "es": ("Tipos de organización", "Startups", "Consultoras", "Etapa de startup · opcional", "Restaurar empresas"),
        }
        for lang, labels in expected.items():
            with self.subTest(lang=lang):
                values = self.page.evaluate(
                    "lang => { localStorage.setItem('pg_lang', lang); return [t('filterCategory'), t('showStartups'), t('showConsultancies'), t('filterStage'), t('clearFilters')]; }",
                    lang,
                )
                self.assertEqual(tuple(values), labels)

    def test_remote_work_mode_filters_verified_types_and_preserves_navigation(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        unverified = dict(next(company for company in companies if company.get("workspace_type")))
        unverified.update(name="Unverified Workspace", lat=-12.1101, lng=-77.0301)
        unverified.pop("sources")
        restricted = dict(next(company for company in companies if company.get("workspace_type")))
        restricted.update(name="Restricted Workspace", lat=-12.1102, lng=-77.0302)
        restricted["sources"] = [dict(restricted["sources"][0], provenance_class="private")]
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies + [unverified, restricted])
        self.page.locator('[data-sort="alpha"]').click()
        self.set_mode("remote")

        expected = [
            company for company in companies
            if company["city"] == "lima" and company.get("workspace_type") in ("coworking", "cafe", "library")
        ]
        self.assertEqual(self.page.locator(".co").count(), len(expected))
        self.assertEqual(self.page.locator(".co-marker").count(), len(expected))
        self.assertEqual(self.page.locator(".co", has_text="Unverified Workspace").count(), 0)
        self.assertEqual(self.page.locator(".co", has_text="Restricted Workspace").count(), 0)
        self.assertTrue(self.page.locator("#viewCategoryField").is_hidden())
        self.assertFalse(self.page.locator("#viewWorkspaceField").is_hidden())
        self.assertTrue(self.page.locator('[data-view-mode="remote"]').is_checked())
        self.assertEqual(self.page.locator('[data-city="lima"]').get_attribute("class"), "barbtn active")
        self.assertEqual(self.page.locator('[data-sort="alpha"]').get_attribute("class"), "barbtn active")

        self.set_workspace_types("cafe", "library")
        expected = [company for company in expected if company["workspace_type"] in ("cafe", "library")]
        self.assertEqual(self.page.locator(".co").count(), len(expected))
        self.assertEqual(set(self.page.locator(".co .tag").all_text_contents()), {"Café", "Biblioteca"})

        self.assertFalse(self.page.locator("#clearViewFilters").is_hidden())
        self.page.locator("#clearViewFilters").click()
        self.assertTrue(self.page.locator('[data-view-mode="remote"]').is_checked())
        self.assertEqual(self.page.locator("[data-workspace-type]").evaluate_all(
            "options => options.filter(option => option.checked).map(option => option.value)"
        ), ["coworking", "cafe", "library"])
        self.assertEqual(self.page.locator(".co").count(), len([
            company for company in companies if company["city"] == "lima" and company.get("workspace_type")
        ]))
        self.assertTrue(self.page.locator("#clearViewFilters").is_hidden())

        self.set_workspace_types()
        self.assertEqual(self.page.locator(".panel-empty").text_content(), "Selecciona al menos un tipo de lugar.")
        self.page.locator("#clearViewFilters").click()
        self.page.locator('[data-city="arequipa"]').click()
        self.assertEqual(
            self.page.locator(".panel-empty").text_content(),
            "Aún no hay lugares con una fuente pública en Arequipa.",
        )
        self.assertTrue(self.page.locator('[data-view-mode="remote"]').is_checked())
        self.page.locator('[data-city="lima"]').click()

        remote_mode = self.page.locator('[data-view-mode="remote"]')
        remote_mode.focus()
        remote_mode.press("ArrowLeft")
        self.assertTrue(self.page.locator('[data-view-mode="ecosystem"]').is_checked())
        self.page.locator('[data-view-mode="ecosystem"]').press("ArrowRight")
        self.assertTrue(remote_mode.is_checked())

        self.set_mode("ecosystem")
        default_expected = [
            company for company in companies
            if company["city"] == "lima" and company["category"] in ("Startup", "Technology Consultancy")
        ]
        self.assertEqual(self.page.locator(".co").count(), len(default_expected))
        self.assertFalse(self.page.locator("#viewCategoryField").is_hidden())
        self.assertTrue(self.page.locator("#viewWorkspaceField").is_hidden())

    def test_remote_work_popup_shows_safe_source_date_without_amenity_claims(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        expected = next(company for company in companies if company["name"] == "WeWork Jorge Basadre 349")
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        self.set_mode("remote")
        self.page.locator(".co", has_text=expected["name"]).click()

        self.assertEqual(self.page.locator(".test-popup .workspace-chip").text_content(), "Coworking")
        self.assertEqual(self.page.locator(".test-popup .source-link").get_attribute("href"), expected["sources"][0]["source_url"])
        self.assertIn("2026", self.page.locator(".test-popup .source-observed").text_content())
        self.assertNotIn("2026-09-09", self.page.locator(".test-popup .source-observed").text_content())
        self.assertEqual(self.page.locator(".test-popup .source-observed").get_attribute("datetime"), expected["sources"][0]["observed_at"])
        popup_text = self.page.locator(".test-popup").text_content().casefold()
        for unsupported_claim in ("wifi", "hours", "horario", "precio", "price"):
            self.assertNotIn(unsupported_claim, popup_text)

        unsafe_urls = (
            "javascript:window.__injected=1",
            "http://www.openstreetmap.org/node/1",
            "https://user:pass@www.openstreetmap.org/node/1",
            "https://localhost/node/1",
            "https://maps.googleapis.com/maps/api/place/1",
            "https://www.openstreetmap.org/node/1?token=secret",
            "https://www.wikipedia.org/wiki/OpenStreetMap",
        )
        for source_url in unsafe_urls:
            with self.subTest(source_url=source_url):
                unsafe = dict(expected, name='<img src=x onerror="window.__injected=1">')
                unsafe["sources"] = [dict(expected["sources"][0], source_url=source_url)]
                self.render(unsafe)
                self.assertEqual(self.page.locator(".test-popup .source-link").count(), 0)
                self.assert_no_injection()

        for provider in ('<svg onload="window.__injected=1">', "Google Maps Platform", "OPENSTREETMAP"):
            with self.subTest(provider=provider):
                unsafe = dict(expected)
                unsafe["sources"] = [dict(expected["sources"][0], provider=provider)]
                self.render(unsafe)
                self.assertEqual(self.page.locator(".test-popup .source-link").count(), 0)
                self.assert_no_injection()

        no_timezone = dict(expected)
        no_timezone["sources"] = [dict(expected["sources"][0], observed_at="2026-09-09T00:00:00")]
        self.render(no_timezone)
        self.assertEqual(self.page.locator(".test-popup .source-link").count(), 0)

    def test_remote_work_controls_have_bilingual_copy_and_mobile_targets(self):
        expected = {
            "en": ("Map mode", "Ecosystem", "Work remotely", "Place types", "Coworking", "Café", "Library", "Location backed by a public source. Wi-Fi and amenities are not yet verified."),
            "es": ("Modo del mapa", "Ecosistema", "Trabajar remoto", "Tipos de lugar", "Coworking", "Café", "Biblioteca", "Ubicación respaldada por una fuente pública. Wi-Fi y servicios aún no verificados."),
        }
        for lang, labels in expected.items():
            with self.subTest(lang=lang):
                values = self.page.evaluate(
                    "lang => { localStorage.setItem('pg_lang', lang); return [t('mapMode'), t('ecosystemMode'), t('remoteWorkMode'), t('filterWorkspace'), t('workspaceCoworking'), t('workspaceCafe'), t('workspaceLibrary'), t('remoteNotice')]; }",
                    lang,
                )
                self.assertEqual(tuple(values), labels)

        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.set_viewport_size({"width": 320, "height": 700})
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        self.set_mode("remote")
        self.assertGreaterEqual(self.page.locator('[data-view-mode="remote"]').locator("xpath=..").bounding_box()["height"], 44)
        for option in self.page.locator("[data-workspace-type]").all():
            self.assertGreaterEqual(option.locator("xpath=..").bounding_box()["height"], 44)
        self.assertLessEqual(
            self.page.locator("#viewWorkspaces").evaluate("el => el.scrollWidth"),
            self.page.locator("#viewWorkspaces").evaluate("el => el.clientWidth"),
        )

    def test_desktop_filter_row_selection_and_popup_leave_panel_as_sidebar(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.set_viewport_size({"width": 1280, "height": 800})
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        self.set_categories("VC")
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

        self.set_categories("Coworking Space")
        self.assertIn("expanded", self.page.locator("#panel").get_attribute("class") or "")
        self.assertGreater(self.page.locator(".co").count(), 0)
        self.page.locator(".co").first.click()
        self.assertEqual(self.page.locator(".test-popup").count(), 1)
        self.assertNotIn("expanded", self.page.locator("#panel").get_attribute("class") or "")

    def test_filter_hierarchy_keyboard_reset_and_mobile_targets(self):
        companies = json.loads((ROOT / "companies.json").read_text(encoding="utf-8"))
        self.page.set_viewport_size({"width": 320, "height": 700})
        self.page.evaluate("data => { ALL_COMPANIES = data; applyCity('lima'); }", companies)
        self.page.locator("#panelHead").evaluate("el => el.click()")
        self.page.locator('[data-city="arequipa"]').click()
        self.page.locator('[data-sort="alpha"]').click()

        category = self.page.locator('[data-view-category="Coworking Space"]')
        stage = self.page.locator('[data-view-stage="Seed"]')
        clear = self.page.locator("#clearViewFilters")
        self.assertFalse(self.page.locator("#viewStageField").is_hidden())
        self.assertTrue(clear.is_hidden())
        self.assertGreaterEqual(category.locator("xpath=..").bounding_box()["height"], 44)

        category.focus()
        category.press("Space")
        self.assertTrue(category.is_checked())
        self.assertFalse(clear.is_hidden())
        self.assertGreater(self.page.locator("#coList").bounding_box()["height"], 0)
        self.assertGreaterEqual(stage.locator("xpath=..").bounding_box()["height"], 44)
        self.assertLessEqual(
            self.page.locator("#viewCategories").evaluate("el => el.scrollWidth"),
            self.page.locator("#viewCategories").evaluate("el => el.clientWidth"),
        )

        stage.focus()
        stage.press("Space")
        self.assertTrue(stage.is_checked())
        self.page.locator('[data-view-category="Startup"]').locator("xpath=..").click()
        self.assertFalse(stage.is_checked())
        self.assertTrue(self.page.locator("#viewStageField").is_hidden())

        clear.click()
        self.assertFalse(category.is_checked())
        self.assertTrue(self.page.locator('[data-view-category="Startup"]').is_checked())
        self.assertTrue(self.page.locator('[data-view-category="Technology Consultancy"]').is_checked())
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
