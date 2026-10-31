import copy
import unittest
from backend.analysis import AnalysisService
from backend.insights import ProviderError
from backend.reports import ReportService, ReportError, build_context


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

    def test_what_if_overflow_is_unavailable_instead_of_nonfinite_json(self):
        self.analysis['encounters'][0]['miss_distance_m']=1e308
        context=build_context(self.analysis)
        scenarios=[x for x in context['what_if_scenarios'] if x['event_id']=='demo-critical-36h' and x['distance_multiplier']==2]
        self.assertTrue(all(x['status']=='unavailable' for x in scenarios))
        self.assertTrue(all(x['assumed_miss_distance_m'] is None for x in scenarios))

    def test_what_if_rewording_cannot_override_remaining_critical_trigger(self):
        def change(result):
            result['what_if_summary']={'text':'Doubling separation yields elevated despite Pc remaining 0.0002.',
                'fact_ids':['scenario.0.distance_larger.resulting_severity']}
        report=self.service(ReportClient(change)).generate(self.analysis)
        self.assertEqual(report['status'],'ready')
        text=report['what_if_summary']['text']
        self.assertIn('separation multiplied by 2 alone yields critical',text)
        self.assertIn('combining both assumptions yields elevated',text)
        self.assertNotIn('despite Pc',text)
        self.assertTrue(any('rewritten AI interpretation' in warning for warning in report['warnings']))

    def test_policy_window_and_derived_scenario_values_are_supported_evidence(self):
        def change(result):
            result['executive_summary']={'text':'There are no critical encounters within 24 hours.', 'fact_ids':['portfolio.critical_within_24h']}
            result['what_if_summary']={'text':'A 90% lower assumed Pc still leaves the 800 m distance trigger active.',
                'fact_ids':['scenario.0.pc_lower.resulting_severity']}
        self.assertEqual(self.service(ReportClient(change)).generate(self.analysis)['status'],'ready')

    def test_captured_live_report_id_capitalization_and_missing_numeric_citation(self):
        def change(result):
            result['executive_summary']={'text':'Demo-critical-36h has predicted Pc 0.0002.', 'fact_ids':['event.0.predicted_pc']}
            result['key_findings'][0]={'text':'The source report count is 3.', 'fact_ids':['portfolio.model_status']}
        report=self.service(ReportClient(change)).generate(self.analysis)
        self.assertEqual(report['status'],'ready')
        self.assertIn('portfolio.source_reports',report['key_findings'][0]['fact_ids'])

    def test_severity_words_do_not_corrupt_other_event_identifiers(self):
        def change(result):
            result['what_if_summary']={'text':'Demo-elevated-12h remains elevated across these assumptions.',
                'fact_ids':['scenario.0.combined.resulting_severity','scenario.1.pc_lower.resulting_severity']}
        self.assertEqual(self.service(ReportClient(change)).generate(self.analysis)['status'],'ready')

    def test_mixed_threshold_direction_claim_is_replaced_with_labeled_facts(self):
        def change(result):
            result['encounters'][2]['assessment']={'text':'Pc and miss distance are both below all thresholds.',
                'fact_ids':['event.2.predicted_pc','event.2.miss_distance_m']}
        report=self.service(ReportClient(change)).generate(self.analysis)
        item=report['priority_events'][2]
        self.assertEqual(item['assessment_status'],'factual_fallback')
        self.assertNotIn('both below',item['assessment']['text'])
        self.assertTrue(any('direction' in w for w in report['warnings']))

    def test_numeric_event_id_cannot_hide_a_fabricated_count(self):
        self.analysis['encounters'][0]['event_id']='987654'
        def change(result):
            result['executive_summary']={'text':'There are 987654 critical encounters.', 'fact_ids':['portfolio.critical']}
        self.assertEqual(self.service(ReportClient(change)).generate(self.analysis)['status'],'unavailable')
        def legitimate(result):
            result['executive_summary']={'text':'Encounter 987654 is critical.', 'fact_ids':['event.0.severity']}
        self.assertEqual(self.service(ReportClient(legitimate)).generate(self.analysis)['status'],'ready')

    def test_plural_and_british_execution_instructions_are_rejected(self):
        for instruction in ['Fire the thrusters now.','Perform a manoeuvre immediately.','Perform a\nmanoeuvre immediately.']:
            def change(result):
                result['encounters'][0]['actions'][0]['rationale']['text']=instruction
            with self.subTest(instruction=instruction):
                self.assertEqual(self.service(ReportClient(change)).generate(self.analysis)['status'],'unavailable')

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
