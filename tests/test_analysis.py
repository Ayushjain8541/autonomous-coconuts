import unittest
from backend.analysis import AnalysisService, AnalysisError

CSV = b'event_id,time_to_tca,miss_distance,relative_speed,risk,relative_position_r,relative_position_t,relative_position_n,relative_velocity_r,relative_velocity_t,relative_velocity_n\nb,4,9000,50,-8,1,2,3,4,5,6\na,3,1500,7500,-7,1500,0,0,0,7500,0\na,2,800,7500,-6,800,0,0,0,7500,0\n'


def valid_model(request):
    return {'model_version': 'test-boundary-v1', 'feature_schema_version': '1',
            'predictions': [{'event_id': e['event_id'], 'predicted_pc': 1e-5,
                             'predicted_log10_pc': -5, 'status': 'ready', 'warnings': []}
                            for e in reversed(request['events'])]}


class AnalysisTests(unittest.TestCase):
    def test_latest_report_and_probability_provenance(self):
        result = AnalysisService(predictor=valid_model).analyze(CSV)
        self.assertEqual(result['source']['mode'], 'uploaded_csv')
        self.assertEqual(result['source']['report_count'], 3)
        a, b = result['encounters']
        self.assertEqual(a['event_id'], 'a')
        self.assertEqual(a['latest_report_id'], 'row-4')
        self.assertEqual(a['time_to_tca_hours'], 48)
        self.assertEqual(a['reported_pc'], 1e-6)
        self.assertEqual(a['predicted_pc'], 1e-5)
        self.assertEqual(a['severity'], 'critical')
        self.assertEqual(b['severity'], 'elevated')
        self.assertEqual(a['geometry']['position_m']['r'], 800)
        self.assertIsNone(a['globe_position'])
        self.assertIsNone(result['scenario_clock_utc'])

    def test_default_model_unavailable_does_not_copy_reported_risk(self):
        result = AnalysisService().analyze(CSV)
        a, b = result['encounters']
        self.assertEqual(result['model']['status'], 'unavailable')
        self.assertIsNone(a['predicted_pc'])
        self.assertEqual(a['reported_pc'], 1e-6)
        self.assertEqual(a['severity'], 'critical')
        self.assertEqual(b['severity'], 'unknown')

    def test_model_id_coverage_and_numerical_contract_are_enforced(self):
        def bad(request):
            d = valid_model(request)
            d['predictions'][0]['predicted_pc'] = 2
            return d
        def missing(request):
            d = valid_model(request); d['predictions'].pop(); return d
        def mismatch(request):
            d = valid_model(request);d['predictions'][0]['predicted_log10_pc'] = -2;return d
        for predictor in [bad, missing, mismatch]:
            with self.subTest(predictor=predictor):
                with self.assertRaises(AnalysisError):
                    AnalysisService(predictor=predictor).analyze(CSV)

    def test_store_expiry_capacity_and_mutation_isolation(self):
        now = [0.0]
        service = AnalysisService(predictor=valid_model, max_analyses=1, ttl_seconds=10, clock=lambda: now[0])
        first = service.analyze(CSV)
        second = service.demo()
        with self.assertRaises(AnalysisError):service.get(first['analysis_id'])
        second['encounters'][0]['severity'] = 'safe'
        self.assertEqual(service.get(second['analysis_id'])['encounters'][0]['severity'], 'critical')
        now[0] = 11
        with self.assertRaises(AnalysisError):service.get(second['analysis_id'])

    def test_demo_has_unique_stored_identity_and_keeps_fixture_flags(self):
        service = AnalysisService()
        first, second = service.demo(), service.demo()
        self.assertNotEqual(first['analysis_id'], second['analysis_id'])
        self.assertEqual(service.get(first['analysis_id'])['source']['mode'], 'synthetic_demo')
        self.assertEqual(first['model']['status'], 'fixture')

    def test_latest_tie_is_explicit_and_partial_geometry_is_not_filled(self):
        raw = b'event_id,time_to_tca,miss_distance,relative_position_r\na,2,800,100\na,2,900,200\n'
        event = AnalysisService(predictor=valid_model).analyze(raw)['encounters'][0]
        self.assertEqual(event['miss_distance_m'], 900)
        self.assertIsNone(event['geometry'])
        self.assertTrue(any('same' in x.lower() or 'tie' in x.lower() for x in event['warnings']))
