"""Public Scout guide: navigation, responsive layout and clipboard outcomes."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

class ScoutPageTests(unittest.TestCase):
    def test_guide_navigation_and_copy_outcomes(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, timeout=20000)
                try:
                    for width in (390, 1440):
                        with self.subTest(width=width):
                            page = browser.new_page(viewport={"width": width, "height": 900})
                            errors = []
                            page.on("pageerror", lambda error: errors.append(str(error)))
                            page.goto(f"http://127.0.0.1:{server.server_port}/scout/", wait_until="domcontentloaded")
                            page.get_by_role("link", name="Empezar con Scout").click(timeout=5000)
                            self.assertTrue(page.url.endswith("#guia"))
                            self.assertFalse(page.evaluate("document.documentElement.scrollWidth > innerWidth"))
                            page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:async text => {window.copied=text;}}})")
                            page.get_by_role("button", name="Copiar comandos para empezar").click()
                            page.wait_for_function("window.copied && window.copied.includes('scout agent status')")
                            page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:async () => {throw Error('denied')}}})")
                            page.get_by_role("button", name="Copiar comando de exportación").click()
                            page.wait_for_function("document.querySelector('[role=status]').textContent.includes('manualmente')")
                            page.get_by_text("API local y OpenAPI", exact=True).click()
                            self.assertTrue(page.get_by_text("ChatGPT en la nube", exact=False).is_visible())
                            self.assertEqual(errors, [])
                            page.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

if __name__ == "__main__":
    unittest.main()
