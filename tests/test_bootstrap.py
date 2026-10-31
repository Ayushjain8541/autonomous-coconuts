import json
import threading
import unittest
import urllib.error
import urllib.request
from backend.server import make_server
from ml.predictor import predict_batch
from ml.rules import classify_encounter


class RuleTests(unittest.TestCase):
    def test_boundaries_and_precedence(self):
        cases = [(1e-4, 8000, "critical"), (1e-8, 999, "critical"),
                 (1e-8, 1000, "elevated"), (1e-8, 5000, "elevated"),
                 (1e-8, 5001, "safe"), (1e-6, 8000, "elevated"),
                 (0, 8000, "safe"), (1e-4, 2000, "critical")]
        for pc, distance, expected in cases:
            with self.subTest(pc=pc, distance=distance):
                self.assertEqual(classify_encounter(pc, distance)["severity"], expected)

    def test_missing_evidence_is_not_safe(self):
        self.assertEqual(classify_encounter(None, 8000)["severity"], "unknown")
        self.assertEqual(classify_encounter(None, 900)["severity"], "critical")
        self.assertEqual(classify_encounter(1e-4, None)["severity"], "critical")

    def test_invalid_values_are_rejected(self):
        for pc, distance in [(2, 8000), (-1, 8000), (float("nan"), 8000),
                             (1e-5, float("inf")), (True, 8000), (0, -1)]:
            with self.subTest(pc=pc, distance=distance):
                with self.assertRaises(ValueError):
                    classify_encounter(pc, distance)

    def test_predictor_does_not_invent_a_model(self):
        data = predict_batch({"schema_version": "1.0", "events": [{"event_id": "a", "reports": []}]})
        self.assertIsNone(data["model_version"])
        self.assertEqual(data["predictions"][0]["status"], "unavailable")
        self.assertIsNone(data["predictions"][0]["predicted_pc"])

    def test_predictor_rejects_bad_or_duplicate_ids(self):
        for request in [None, {}, {"schema_version": "1.0", "events": [{"event_id": "a"}, {"event_id": "a"}]}]:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    predict_batch(request)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = "http://127.0.0.1:%s" % cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get(self, path):
        return urllib.request.urlopen(self.base + path, timeout=3)

    def test_health_is_honest_about_missing_integrations(self):
        with self.get("/api/health") as response:
            data = json.load(response)
        self.assertEqual(data["model"], "unavailable")
        self.assertEqual(data["insights"], "unconfigured")

    def test_fixture_round_trip_and_global_alert_semantics(self):
        with self.get("/api/demo") as response:
            data = json.load(response)
        self.assertEqual(data["source"]["mode"], "synthetic_demo")
        self.assertEqual(data["model"]["status"], "fixture")
        critical = [x for x in data["encounters"] if x["severity"] == "critical"]
        self.assertEqual(critical[0]["time_to_tca_hours"], 36)
        self.assertFalse([x for x in critical if x["time_to_tca_hours"] <= 24])
        self.assertIsNotNone(critical[0]["geometry"])

    def test_only_allowlisted_web_assets_are_served(self):
        for path in ["/", "/app.js", "/styles.css"]:
            with self.get(path) as response:
                self.assertEqual(response.status, 200)
        for path in ["/.env", "/AGENTS.md", "/../.git/config", "/contracts/fixtures/analysis-demo.json"]:
            with self.subTest(path=path):
                with self.assertRaises(urllib.error.HTTPError) as error:
                    self.get(path)
                self.assertEqual(error.exception.code, 404)

    def test_unimplemented_integrations_are_not_fake_successes(self):
        for path, expected in [("/api/analyses", "MODEL_UNAVAILABLE"),
                                ("/api/analyses/demo/insights", "INSIGHTS_UNAVAILABLE")]:
            req = urllib.request.Request(self.base + path, data=b"{}", headers={"Content-Type": "application/json"})
            with self.subTest(path=path):
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(req, timeout=3)
                self.assertEqual(error.exception.code, 503)
                self.assertEqual(json.load(error.exception)["error"]["code"], expected)


if __name__ == "__main__":
    unittest.main()
