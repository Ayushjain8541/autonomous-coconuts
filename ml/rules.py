"""Deterministic hackathon-brief tiers. Not certified operational safety logic."""
import math
from numbers import Real


def classify_encounter(predicted_pc, miss_distance_m):
    for name, value in (("predicted_pc", predicted_pc), ("miss_distance_m", miss_distance_m)):
        if value is not None and (isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) or value < 0):
            raise ValueError(name + " must be a finite nonnegative number or null")
    if predicted_pc is not None and predicted_pc > 1:
        raise ValueError("predicted_pc must be <= 1")
    reasons = []
    def add(rule_id, field, operator, value, threshold, unit):
        reasons.append(dict(rule_id=rule_id, field=field, operator=operator,
                            value=value, threshold=threshold, unit=unit))
    if predicted_pc is not None and predicted_pc >= 1e-4:
        add("PC_CRITICAL", "predicted_pc", ">=", predicted_pc, 1e-4, "probability")
    if miss_distance_m is not None and miss_distance_m < 1000:
        add("MISS_DISTANCE_CRITICAL", "miss_distance_m", "<", miss_distance_m, 1000, "m")
    if reasons:
        return {"severity": "critical", "flag_reasons": reasons}
    if predicted_pc is None or miss_distance_m is None:
        return {"severity": "unknown", "flag_reasons": [{"rule_id": "MISSING_EVIDENCE", "field": "predicted_pc,miss_distance_m"}]}
    if predicted_pc >= 1e-6:
        add("PC_ELEVATED", "predicted_pc", ">=", predicted_pc, 1e-6, "probability")
    if miss_distance_m <= 5000:
        add("MISS_DISTANCE_ELEVATED", "miss_distance_m", "<=", miss_distance_m, 5000, "m")
    if reasons:
        return {"severity": "elevated", "flag_reasons": reasons}
    return {"severity": "safe", "flag_reasons": [{"rule_id": "SAFE_COMBINED", "field": "predicted_pc,miss_distance_m"}]}
