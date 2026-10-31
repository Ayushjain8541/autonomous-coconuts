"""Upload-to-assessment orchestration; numerical ownership stays at the ML boundary."""
import copy
import json
import math
import threading
import time
import uuid
from collections import OrderedDict
from numbers import Real
from pathlib import Path
import ml
from .model_adapter import predict_batch
from .ingestion import parse_csv

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'Per-report collision probability estimated from the latest telemetry report; not a final-TCA forecast'


class AnalysisError(ValueError):
    def __init__(self, message, code='INTERNAL_ERROR', status=502):
        super().__init__(message)
        self.code, self.status = code, status
        self.details = []


def _number(value):
    return not isinstance(value, bool) and isinstance(value, Real) and math.isfinite(value)


def _validate_predictions(batch, ids):
    if not isinstance(batch, dict) or not isinstance(batch.get('predictions'), list):
        raise AnalysisError('Model response does not match the shared batch contract.')
    outputs = {}
    for item in batch['predictions']:
        if not isinstance(item, dict) or not isinstance(item.get('event_id'), str) or item['event_id'] in outputs:
            raise AnalysisError('Model response has invalid or duplicate event IDs.')
        status = item.get('status')
        pc, log = item.get('predicted_pc'), item.get('predicted_log10_pc')
        warnings = item.get('warnings')
        if status not in {'ready', 'unavailable'} or not isinstance(warnings, list) or any(not isinstance(x, str) for x in warnings):
            raise AnalysisError('Model status/warnings do not match the shared contract.')
        if status == 'unavailable':
            if pc is not None or log is not None:
                raise AnalysisError('Unavailable predictions must have null probabilities.')
        else:
            if not batch.get('model_version') or not isinstance(batch['model_version'], str):
                raise AnalysisError('Ready predictions require a model version.')
            if not _number(pc) or not 0 <= pc <= 1:
                raise AnalysisError('Model returned an invalid probability.')
            if log is not None and (not _number(log) or log > 0 or not math.isclose(10 ** log, pc, rel_tol=1e-6, abs_tol=0)):
                raise AnalysisError('Model probability and log-risk are inconsistent.')
            pc = float(pc)
            log = float(log) if log is not None else (math.log10(pc) if pc else None)
        outputs[item['event_id']] = dict(item, predicted_pc=pc, predicted_log10_pc=log)
    if set(outputs) != set(ids):
        raise AnalysisError('Model response event IDs do not exactly match the requested events.')
    for key in ['model_version', 'feature_schema_version']:
        if batch.get(key) is not None and not isinstance(batch[key], str):
            raise AnalysisError('Model metadata must be strings or null.')
    return outputs


class AnalysisService:
    def __init__(self, predictor=None, classifier=None, max_analyses=32, ttl_seconds=3600, clock=time.monotonic):
        self.predictor = predictor or predict_batch
        self.classifier = classifier or ml.classify_encounter
        self.max_analyses, self.ttl_seconds, self.clock = max_analyses, ttl_seconds, clock
        self._items, self._lock = OrderedDict(), threading.RLock()
        self.model_status = 'unavailable'

    def _prune(self):
        now = self.clock()
        for key in list(self._items):
            if now - self._items[key][0] >= self.ttl_seconds:
                del self._items[key]

    def _save(self, result):
        with self._lock:
            self._prune()
            self._items[result['analysis_id']] = (self.clock(), copy.deepcopy(result))
            while len(self._items) > self.max_analyses:
                self._items.popitem(last=False)
        return result

    def get(self, analysis_id):
        with self._lock:
            self._prune()
            if analysis_id not in self._items:
                raise AnalysisError('Analysis not found or expired; load/upload it again.', 'ANALYSIS_NOT_FOUND', 404)
            return copy.deepcopy(self._items[analysis_id][1])

    def demo(self):
        result = json.loads((ROOT / 'contracts/fixtures/analysis-demo.json').read_text())
        result['analysis_id'] = uuid.uuid4().hex
        for event in result['encounters']:
            event.update(self.classifier(event['predicted_pc'], event['miss_distance_m']))
        return self._save(result)

    def analyze(self, raw):
        parsed = parse_csv(raw)
        eligible = [{'event_id': e['event_id'], 'reports': [min(e['reports'],
                     key=lambda r: (r['fields']['time_to_tca'], -int(r['report_id'][4:])))]}
                    for e in parsed['events']]
        try:
            batch = self.predictor({'schema_version': '1.0', 'events': eligible})
        except Exception:
            raise AnalysisError('The P3 model adapter failed; check its artifact/runtime setup.', 'MODEL_UNAVAILABLE', 503) from None
        outputs = _validate_predictions(batch, [e['event_id'] for e in eligible])
        eligible_by_id = {e['event_id']: e['reports'] for e in eligible}
        encounters = []
        for event in parsed['events']:
            reports = event['reports']
            latest = min(reports, key=lambda r: (r['fields']['time_to_tca'], -int(r['report_id'][4:])))
            fields = latest['fields']
            warnings = []
            if sum(r['fields']['time_to_tca'] == fields['time_to_tca'] for r in reports) > 1:
                warnings.append('Multiple reports have the same latest time; the last CSV record is displayed. Source records are preserved.')
            prediction = outputs[event['event_id']]
            warnings.extend(prediction['warnings'])
            position = {k: fields.get('relative_position_' + k) for k in ['r', 't', 'n']}
            velocity = {k: fields.get('relative_velocity_' + k) for k in ['r', 't', 'n']}
            position = position if all(x is not None for x in position.values()) else None
            velocity = velocity if all(x is not None for x in velocity.values()) else None
            geometry = {'frame': 'RTN', 'position_m': position, 'velocity_mps': velocity} if position or velocity else None
            used = eligible_by_id.get(event['event_id'], []) if prediction['status']=='ready' else []
            assessment = {'event_id': event['event_id'], 'mission_id': fields.get('mission_id'),
                          'report_count': len(reports), 'latest_report_id': latest['report_id'],
                          'report_ids': [r['report_id'] for r in reports],
                          'prediction_report_ids': [r['report_id'] for r in used],
                          'time_to_tca_hours': fields['time_to_tca'] * 24,
                          'reported_pc': 10 ** fields['risk'] if fields.get('risk') is not None else None,
                          'predicted_pc': prediction['predicted_pc'], 'predicted_log10_pc': prediction['predicted_log10_pc'],
                          'prediction_status': prediction['status'], 'miss_distance_m': fields['miss_distance'],
                          'relative_speed_mps': fields.get('relative_speed'), 'geometry': geometry,
                          'globe_position': None, 'warnings': warnings}
            assessment.update(self.classifier(assessment['predicted_pc'], assessment['miss_distance_m']))
            encounters.append(assessment)
        status = 'ready' if any(e['prediction_status'] == 'ready' for e in encounters) else 'unavailable'
        self.model_status = status
        result = {'schema_version': '1.0', 'analysis_id': uuid.uuid4().hex,
                  'source': {'mode': 'uploaded_csv', 'label': 'Uploaded historical encounter reports',
                             'sha256': parsed['source_sha256'], 'report_count': parsed['report_count']},
                  'time_basis': 'per_event_latest_report', 'scenario_clock_utc': None,
                  'model': {'version': batch.get('model_version'), 'status': status, 'target': TARGET,
                            'feature_schema_version': batch.get('feature_schema_version')},
                  'encounters': encounters,
                  'warnings': ['Lead times are measured at each encounter\'s latest report; historical events do not share a current clock.',
                               'Source miss distance is a report prediction at TCA; global orbit positions are unavailable.']}
        if status == 'unavailable':
            result['warnings'].append('No learned prediction is available. Reported risk is not substituted for model output.')
        return self._save(result)
