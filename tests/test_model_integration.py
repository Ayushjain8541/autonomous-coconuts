import importlib.util
import unittest
from unittest.mock import patch
from backend.analysis import AnalysisService
from backend.model_adapter import predict_batch

HEADER='event_id,time_to_tca,miss_distance,relative_speed,relative_position_r,relative_position_t,relative_position_n,c_object_type,c_sigma_r,t_sigma_r,F10,AP,risk'
CSV=(HEADER+'\n123,3,9000,7500,9000,0,0,DEBRIS,20,30,100,5,-1\n123,0.5,800,7500,800,0,0,DEBRIS,20,30,100,5,-2\n').encode()


class ModelIntegrationTests(unittest.TestCase):
    def test_latest_report_is_scored_inside_48h_without_target_columns(self):
        captured=[]
        def score(rows):
            captured.extend(rows)
            return [-7]
        with patch('backend.model_adapter._score_rows',score):
            result=AnalysisService().analyze(CSV)
        event=result['encounters'][0]
        self.assertEqual(captured[0]['time_to_tca'],.5)
        self.assertNotIn('risk',captured[0])
        self.assertEqual(len(captured),1)
        self.assertEqual(event['prediction_report_ids'],[event['latest_report_id']])
        self.assertEqual(event['predicted_pc'],1e-7)
        self.assertEqual(event['reported_pc'],1e-2)
        self.assertEqual(event['severity'],'critical')
        self.assertEqual(result['model']['status'],'ready')
        self.assertIn('Per-report',result['model']['target'])

    def test_missing_features_and_unsupported_ids_do_not_become_fake_predictions(self):
        raw=CSV.replace(b'123,',b'not-numeric,')
        with patch('backend.model_adapter._score_rows') as scorer:
            result=AnalysisService().analyze(raw)
            scorer.assert_not_called()
        event=result['encounters'][0]
        self.assertEqual(event['event_id'],'not-numeric')
        self.assertEqual(event['prediction_status'],'unavailable')
        self.assertIsNone(event['predicted_pc'])
        self.assertEqual(event['prediction_report_ids'],[])
        self.assertEqual(event['severity'],'critical')

    def test_missing_native_runtime_keeps_distance_assessment_available(self):
        with patch('backend.model_adapter._score_rows',side_effect=ImportError('missing runtime')):
            result=AnalysisService().analyze(CSV)
        event=result['encounters'][0]
        self.assertIsNone(event['predicted_pc'])
        self.assertTrue(any('requirements-full' in w for w in event['warnings']))
        self.assertEqual(event['severity'],'critical')

    def test_invalid_model_predictions_are_rejected(self):
        for logs in [[],[float('nan')],[.1]]:
            with self.subTest(logs=logs),patch('backend.model_adapter._score_rows',return_value=logs):
                with self.assertRaises(ValueError):
                    from backend.ingestion import parse_csv
                    request=parse_csv(CSV)
                    request['schema_version']='1.0'
                    request['events'][0]['reports']=[request['events'][0]['reports'][-1]]
                    predict_batch(request)

    @unittest.skipUnless(importlib.util.find_spec('xgboost') and importlib.util.find_spec('pandas'), 'Optional native model runtime is not installed')
    def test_saved_p3_artifact_runs_through_the_api_service_on_a_near_term_report(self):
        result=AnalysisService().analyze(CSV)
        event=result['encounters'][0]
        self.assertEqual(result['model']['status'],'ready')
        self.assertEqual(event['time_to_tca_hours'],12)
        self.assertEqual(event['prediction_status'],'ready')
        self.assertEqual(event['prediction_report_ids'],['row-3'])
        self.assertGreaterEqual(event['predicted_pc'],0)
        self.assertLessEqual(event['predicted_pc'],1)
        self.assertEqual(event['severity'],'critical')

    def test_real_precision_probabilities_survive_the_grounded_briefing_check(self):
        from backend.llm_context import event_evidence, _statement
        with patch('backend.model_adapter._score_rows',return_value=[-6.8278483]):
            event=AnalysisService().analyze(CSV)['encounters'][0]
        facts={};context=event_evidence(event,'event.0',facts)
        result=_statement({'text':context['reference_assessment'],
                           'fact_ids':list(context['fact_ids'].values())},facts,event['event_id'])
        self.assertIn('Assessment:',result['text'])

    def test_report_time_display_is_supported_without_relaxing_numeric_validation(self):
        from backend.llm_context import event_evidence, _statement, ProviderError
        with patch('backend.model_adapter._score_rows',return_value=[-7]):
            event=AnalysisService().analyze(CSV)['encounters'][0]
        event['time_to_tca_hours']=48.0370875
        facts={};context=event_evidence(event,'event.0',facts)
        refs=[context['fact_ids']['time_to_tca_hours']]
        _statement({'text':'The source lead time is 48.04 hours.', 'fact_ids':refs},facts,event['event_id'])
        with self.assertRaises(ProviderError):
            _statement({'text':'The source lead time is 47.04 hours.', 'fact_ids':refs},facts,event['event_id'])

    def test_cohort_count_completion_requires_all_detailed_members(self):
        import copy
        from backend.reports import build_context
        from backend.llm_context import _statement, ProviderError
        analysis=AnalysisService().demo()
        for i in range(7):
            event=copy.deepcopy(analysis['encounters'][0]);event['event_id']='extra-%s'%i
            analysis['encounters'].append(event)
        analysis['source']['report_count']=10
        context=build_context(analysis)
        refs=[event['fact_ids']['severity'] for event in context['priority_encounters']]
        statement={'text':'There are 10 detailed encounters.', 'fact_ids':refs}
        result=_statement(statement,context['facts'])
        self.assertIn('portfolio.detailed_count',result['fact_ids'])
        with self.assertRaises(ProviderError):
            _statement(dict(statement,fact_ids=refs[:-1]),context['facts'])
