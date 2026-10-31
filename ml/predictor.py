"""Replaceable P3 adapter; explicitly unavailable until a real model is supplied."""

def predict_batch(request):
    events = request.get("events") if isinstance(request, dict) else None
    if not isinstance(request, dict) or request.get("schema_version") != "1.0" or not isinstance(events, list):
        raise ValueError("Expected v1 events array")
    ids = [event.get("event_id") for event in events if isinstance(event, dict)]
    if len(ids) != len(events) or any(not isinstance(x, str) or not x for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("Events require unique nonempty string IDs")
    return {"model_version": None, "feature_schema_version": None,
            "predictions": [{"event_id": event_id, "predicted_pc": None,
                             "predicted_log10_pc": None, "status": "unavailable",
                             "warnings": ["No trained model installed. P3 owns this adapter."]}
                            for event_id in ids]}
