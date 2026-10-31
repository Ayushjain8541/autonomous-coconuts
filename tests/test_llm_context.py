"""Ordinary operator cases for shared LLM context, not model accuracy tests."""
import copy
import unittest
import ml
from backend.analysis import AnalysisService
from backend.llm_context import build_analysis_context, event_evidence, provider_context, _statement, ProviderError
from backend.reports import build_context


class LLMContextTests(unittest.TestCase):
    def setUp(self):
        self.analysis = AnalysisService().demo()

    def event(self, pc, distance, hours=36):
        event = copy.deepcopy(self.analysis['encounters'][0])
        event.update(predicted_pc=pc, miss_distance_m=distance, time_to_tca_hours=hours)
        event.update(ml.classify_encounter(pc, distance))
        return event

    def test_probability_only_distance_only_and_missing_pc_preserve_exact_reasons(self):
        cases = [(2e-4, 6000, 'PC_CRITICAL', '>='),
                 (1e-8, 800, 'MISS_DISTANCE_CRITICAL', '<'),
                 (None, 800, 'MISS_DISTANCE_CRITICAL', '<'),
                 (None, 6000, 'MISSING_EVIDENCE', None)]
        for pc, distance, rule_id, operator in cases:
            with self.subTest(rule=rule_id, pc=pc):
                facts = {}
                event = self.event(pc, distance)
                context = event_evidence(event, 'event.0', facts)
                reason = context['classification_reasons'][0]
                self.assertEqual(reason['rule_id'], rule_id)
                self.assertEqual(reason.get('operator'), operator)
                if operator:
                    self.assertEqual(facts[reason['threshold_fact_id']]['value'], reason['threshold'])
                    self.assertEqual(facts[reason['value_fact_id']]['value'], reason['value'])

    def test_critical_beyond_window_is_not_downgraded(self):
        context = build_context(self.analysis)
        event = context['priority_encounters'][0]
        self.assertFalse(event['within_24h'])
        self.assertEqual(context['facts'][event['fact_ids']['severity']]['value'], 'critical')
        self.assertEqual(context['statistics']['critical_within_24h'], 0)

    def test_historical_time_model_identity_and_missing_evidence_are_explicit(self):
        self.analysis['time_basis'] = 'report_lead_time'
        self.analysis['model'] = {'status': 'unavailable', 'version': 'provided-version', 'target': 'Per-report Pc'}
        context = build_analysis_context(self.analysis)
        self.assertEqual(context['model'], self.analysis['model'])
        self.assertIn('not a countdown from now', context['time_interpretation'])
        self.assertFalse(context['evidence_available']['risk_history'])
        self.assertFalse(context['evidence_available']['calibration_metrics'])
        self.assertFalse(context['evidence_available']['maneuver_feasibility'])

    def test_reported_prediction_difference_does_not_become_a_trend(self):
        facts = {}
        event = self.event(2e-4, 6000)
        event['reported_pc'] = 1e-5
        context = event_evidence(event, 'event.0', facts)
        self.assertEqual(context['comparison_interpretation'], 'Different estimates; not an observed risk trend.')
        self.assertEqual(facts[context['fact_ids']['reported_pc']]['value'], 1e-5)

    def test_partial_geometry_is_distinguished_from_complete_geometry(self):
        event = self.event(2e-4, 6000)
        event['geometry']['velocity_mps'] = None
        evidence = event_evidence(event, 'event.0', {})
        self.assertTrue(evidence['geometry_available']['relative_position'])
        self.assertFalse(evidence['geometry_available']['relative_velocity'])
        self.analysis['encounters'] = [event]
        actions = build_context(self.analysis)['priority_encounters'][0]['allowed_actions']
        self.assertIn('CHECK_GEOMETRY', {action['action_id'] for action in actions})

    def test_independent_what_ifs_keep_remaining_critical_trigger(self):
        context = build_context(self.analysis)
        scenarios = {s['scenario_id']: s for s in context['what_if_scenarios'] if s['event_id'] == 'demo-critical-36h'}
        self.assertEqual(scenarios['pc_lower']['resulting_severity'], 'critical')
        self.assertEqual(scenarios['pc_lower']['flag_reasons'][0]['field'], 'miss_distance_m')
        self.assertEqual(scenarios['distance_larger']['resulting_severity'], 'critical')
        self.assertEqual(scenarios['distance_larger']['flag_reasons'][0]['field'], 'predicted_pc')
        self.assertEqual(scenarios['combined']['resulting_severity'], 'elevated')

    def test_supplied_example_value_is_not_a_missing_prediction(self):
        context = event_evidence(self.event(2e-4, 6000), 'event.0', {})
        self.assertTrue(context['value_availability']['predicted_pc'])
        self.assertIn('example Pc value is supplied', context['prediction_evidence'])
        self.assertNotIn('Pc is unavailable', context['reference_assessment'])

    def test_unknown_baseline_preserves_available_separation(self):
        context = event_evidence(self.event(None, 6000), 'event.0', {})
        self.assertFalse(context['value_availability']['predicted_pc'])
        self.assertTrue(context['value_availability']['miss_distance_m'])
        self.assertIn('closest separation is 6000 m', context['reference_assessment'])
        self.assertIn('from the reference', context['reference_assessment'])

    def test_provider_payload_omits_internal_bookkeeping_without_mutating_facts(self):
        context = build_context(self.analysis)
        transmitted = provider_context(context)
        key = 'event.0.predicted_pc'
        self.assertEqual(transmitted['facts'][key], {'value': 2e-4, 'unit': 'probability'})
        self.assertIn('supporting_numbers', context['facts'][key])
        self.assertEqual(transmitted['operations_context']['model'], self.analysis['model'])

    def test_counterfactual_focus_includes_both_remaining_triggers(self):
        context = build_context(self.analysis)
        self.assertEqual(context['what_if_focus_event_ids'][0], 'demo-critical-36h')
        example = context['what_if_interpretations'][0]
        self.assertEqual(example['baseline_severity'], 'critical')
        self.assertEqual(example['outcomes']['pc_lower']['remaining_critical_triggers'], ['miss_distance_m'])
        self.assertEqual(example['outcomes']['distance_larger']['remaining_critical_triggers'], ['predicted_pc'])
        self.assertEqual(example['outcomes']['combined']['resulting_severity'], 'elevated')

    def test_normal_probability_threshold_percentage_has_source_evidence(self):
        facts = {}
        event = self.event(2e-4, 6000)
        context = event_evidence(event, 'event.0', facts)
        threshold_id = context['classification_reasons'][0]['threshold_fact_id']
        result = _statement({'text': 'The critical probability criterion is 0.01%.',
                             'fact_ids': [threshold_id]}, facts, event['event_id'])
        self.assertIn(threshold_id, result['fact_ids'])

    def test_missing_probability_caution_is_allowed_without_claiming_zero_risk(self):
        facts = {}
        event = self.event(None, 6000)
        context = event_evidence(event, 'event.0', facts)
        refs = [context['fact_ids']['predicted_pc']]
        for caution in ['Absence of a probability value is not zero risk.',
                        'Missing Pc does not imply zero risk.', 'This assessment cannot guarantee zero risk.']:
            with self.subTest(caution=caution):
                _statement({'text': caution, 'fact_ids': refs}, facts)
        with self.assertRaises(ProviderError):
            _statement({'text': 'This assessment establishes zero risk.', 'fact_ids': refs}, facts)
