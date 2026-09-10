import unittest

from scripts.benchmark_performance import final_navigation_network


class FinalNavigationNetworkTests(unittest.TestCase):
    @staticmethod
    def recorder(*urls):
        class Recorder:
            def summarize(self, _origin):
                return {"responses": [{"url": url} for url in urls]}

        return Recorder()

    def test_accepts_exactly_one_request_for_each_dataset(self):
        summary = final_navigation_network(
            self.recorder(
                "http://perugrid.test/companies.json",
                "http://perugrid.test/ticker.json",
            ),
            "http://perugrid.test/",
            "test navigation",
        )

        self.assertEqual(len(summary["responses"]), 2)

    def test_rejects_a_duplicate_discovered_at_navigation_end(self):
        with self.assertRaisesRegex(RuntimeError, "completed test navigation"):
            final_navigation_network(
                self.recorder(
                    "http://perugrid.test/companies.json",
                    "http://perugrid.test/companies.json?late=1",
                    "http://perugrid.test/ticker.json",
                ),
                "http://perugrid.test/",
                "test navigation",
            )


if __name__ == "__main__":
    unittest.main()
