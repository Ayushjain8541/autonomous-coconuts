"""P2 bridge to P3's frozen per-report predictor; no training or rule changes."""
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parents[1] / 'prediction/artifacts'


@lru_cache(maxsize=4)
def _identity(model_path, model_mtime, encoder_path, encoder_mtime):
    model = hashlib.sha256(Path(model_path).read_bytes()).hexdigest()
    encoder = hashlib.sha256(Path(encoder_path).read_bytes()).hexdigest()
    return 'xgboost-row-' + model[:16], 'encoder-' + encoder[:16]


def _score_rows(rows):
    import pandas as pd
    from prediction.predict import predict_dataframe
    return predict_dataframe(pd.DataFrame(rows))['risk'].tolist()


def predict_batch(request):
    events = request['events']
    predictions = [{'event_id': e['event_id'], 'predicted_pc': None,
                    'predicted_log10_pc': None, 'status': 'unavailable', 'warnings': []} for e in events]
    batch = {'model_version': None, 'feature_schema_version': None, 'predictions': predictions}
    try:
        encoder = ARTIFACTS / 'feature_encoder.json'
        model = ARTIFACTS / 'collision_risk_model.ubj'
        features = json.loads(encoder.read_text())['features']
        batch['model_version'], batch['feature_schema_version'] = _identity(
            str(model), model.stat().st_mtime_ns, str(encoder), encoder.stat().st_mtime_ns)
    except (OSError, ValueError, KeyError):
        for prediction in predictions:
            prediction['warnings'] = ['Saved model artifacts are unavailable; no risk value was substituted.']
        return batch
    rows, eligible = [], []
    for event, prediction in zip(events, predictions):
        fields = event['reports'][0]['fields']
        missing = [name for name in features if name not in fields]
        if missing:
            prediction['warnings'] = ['Model input columns are missing: ' + ', '.join(missing) + '.']
            continue
        try:
            identifier = float(fields['event_id'])
            if not math.isfinite(identifier) or abs(identifier) > 3.4028234663852886e38:
                raise ValueError()
        except (ValueError, TypeError, OverflowError):
            prediction['warnings'] = ['This trained model requires a finite numeric event ID; the original ID is preserved.']
            continue
        # Target-derived columns never enter P3's feature frame.
        rows.append({name: fields[name] for name in features})
        eligible.append(prediction)
    if not rows:
        return batch
    try:
        logs = _score_rows(rows)
    except (ImportError, OSError):
        for prediction in eligible:
            prediction['warnings'] = ['Model runtime unavailable. Install backend/requirements-full.txt in the server environment.']
        return batch
    if len(logs) != len(eligible) or any(not math.isfinite(x) or x > 0 for x in logs):
        raise ValueError('Predictor must return one finite nonpositive log10(Pc) per selected report.')
    for prediction, log in zip(eligible, logs):
        prediction.update(predicted_pc=10 ** float(log), predicted_log10_pc=float(log), status='ready')
    return batch
