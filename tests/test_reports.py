import copy
import unittest
from backend.analysis import AnalysisService
from backend.insights import ProviderError
from backend.reports import ReportService, ReportError


class ReportClient:
    cache_identity = 'fake-report-client'
    def __init__(self, change=None):
        self.change, self.calls = change, 0
    def generate_structured(self, system, content, schema, max_tokens=4096):
        self.calls += 1
        self.content = content
        if self.change == 'failure':raise ProviderError('Provider unavailable for test.')
        result = {
            'executive_summary': {'text': 'Prioritize the critical encounters while keeping gaps in prediction evidence visible.',
                                  'fact_ids': ['portfolio.critical', 'portfolio.predictions_unavailable']},
            'key_findings': [{'text': 'Review both urgency and severity when allocating operator attention.',
                              'fact_ids': ['portfolio.total']},
                             {'text':'Missing model evidence must remain visible.', 'fact_ids':['portfolio.predictions_unavailable']}],
            'what_if_summary': {'text':'The combined assumptions change the rule result; they do not establish an achievable maneuver.',
                                'fact_ids':['scenario.0.combined.resulting_severity']},
            'encounters': []}
        for event in content['priority_encounters']:
            refs = [event['fact_ids']['severity']]
            result['encounters'].append({'event_id': event['event_id'],
                'assessment': {'text': 'Review the classification together with its supporting evidence.', 'fact_ids': refs},
                'actions': [{'action_id': event['allowed_actions'][0]['action_id'],
                             'rationale': {'text': 'This is an operator review step supported by the encounter assessment.', 'fact_ids': refs}}]})
        if callable(self.change):self.change(result)
        return result


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.analysis = AnalysisService().demo()
    def service(self, client):return ReportService(client_factory=lambda:client)

    def test_generates_actual_narrative_with_references_and_advisory_actions(self):
        client = ReportClient(); result = self.service(client).generate(self.analysis)
        self.assertEqual(result['status'], 'ready')
        self.assertIn('Prioritize', result['executive_summary']['text'])
        self.assertEqual(result['statistics']['total_encounters'], 3)
        self.assertEqual(result['statistics']['severity_counts']['critical'], 1)
        self.assertEqual(result['priority_events'][0]['event_id'], 'demo-critical-36h')
        self.assertTrue(result['priority_events'][0]['actions'][0]['label'])
        self.assertEqual(result['source']['mode'], 'synthetic_demo')
        self.assertTrue(any('Synthetic' in x for x in result['limitations']))
        self.assertTrue(any('maneuver' in x.lower() for x in result['limitations']))
        self.assertNotIn('api_key', str(client.content))

    def test_counts_cover_whole_portfolio_but_model_context_is_bounded(self):
        for i in range(15):
            event = copy.deepcopy(self.analysis['encounters'][0]);event['event_id']='extra-%s'%i
            self.analysis['encounters'].append(event)
        client = ReportClient(); result = self.service(client).generate(self.analysis)
        self.assertEqual(result['statistics']['total_encounters'], 18)
        self.assertEqual(result['statistics']['severity_counts']['critical'], 16)
        self.assertEqual(len(client.content['priority_encounters']), 10)
        self.assertEqual(result['coverage']['omitted_encounters'], 8)

    def test_what_if_reapplies_rules_without_claiming_a_maneuver_or_prediction(self):
        result=self.service(ReportClient()).generate(self.analysis)
        cases={x['scenario_id']:x for x in result['what_if_scenarios'] if x['event_id']=='demo-critical-36h'}
        self.assertEqual(cases['pc_lower']['resulting_severity'],'critical')
        self.assertEqual(cases['distance_larger']['resulting_severity'],'critical')
        self.assertEqual(cases['combined']['resulting_severity'],'elevated')
        self.assertEqual(cases['combined']['status'],'hypothetical')
        self.assertEqual(self.analysis['encounters'][0]['predicted_pc'],.0002)
        self.assertTrue(result['what_if_summary']['fact_ids'])

    def test_bad_references_numbers_cross_event_actions_and_burn_instructions_rejected(self):
        changes = [
            lambda r:r['executive_summary'].update(fact_ids=['invented.fact']),
            lambda r:r['executive_summary'].update(text='There are 987654 critical encounters.'),
            lambda r:r['encounters'][0]['actions'][0].update(action_id='EXECUTE_BURN'),
            lambda r:r['encounters'][0]['assessment'].update(text='Execute a burn now.'),
            lambda r:r['encounters'][0]['assessment'].update(fact_ids=['event.1.severity']),
        ]
        for change in changes:
            with self.subTest(change=change):
                result=self.service(ReportClient(change)).generate(self.analysis)
                self.assertEqual(result['status'],'unavailable')
                self.assertEqual(result['priority_events'],[])
                self.assertTrue(result['warnings'])

    def test_unavailable_prediction_stays_unknown_with_explicit_coverage(self):
        for event in self.analysis['encounters']:
            event.update(prediction_status='unavailable',predicted_pc=None,severity='unknown',flag_reasons=[])
        self.analysis['model']['status']='unavailable';self.analysis['time_basis']='per_event_latest_report'
        result=self.service(ReportClient()).generate(self.analysis)
        self.assertEqual(result['statistics']['prediction_counts']['unavailable'],3)
        self.assertEqual(result['statistics']['severity_counts']['safe'],0)
        self.assertTrue(any('clock' in x.lower() for x in result['limitations']))

    def test_cache_and_exact_report_retrieval_are_isolated(self):
        client=ReportClient();service=self.service(client)
        first=service.generate(self.analysis);second=service.generate(self.analysis)
        self.assertEqual(client.calls,1);self.assertEqual(first['report_id'],second['report_id'])
        first['statistics']['total_encounters']=999
        stored=service.get(self.analysis['analysis_id'],second['report_id'])
        self.assertEqual(stored['statistics']['total_encounters'],3)
        with self.assertRaises(ReportError):service.get('another-analysis',second['report_id'])

    def test_failure_report_is_exportable_but_not_cached_as_success(self):
        client=ReportClient('failure');service=self.service(client)
        first=service.generate(self.analysis);second=service.generate(self.analysis)
        self.assertEqual(first['status'],'unavailable');self.assertIsNone(first['executive_summary'])
        self.assertEqual(client.calls,2)
        self.assertEqual(service.get(self.analysis['analysis_id'],first['report_id'])['statistics']['total_encounters'],3)
