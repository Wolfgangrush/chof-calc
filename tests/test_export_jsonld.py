import json
from chof_calc.export_jsonld import to_jsonld, to_jsonld_str

SAMPLE = {
    "system": "mq9",
    "h_quantity": 70.35,
    "severity": "high",
    "transparency_class": "glass_box",
    "h_modality": {"ex_ante_constraint": 0.34, "in_flight_supervision": 0.33, "ex_post_audit": 0.33},
    "h_latency_profile": {"observe": 0.3, "orient": 0.3, "decide": 0.25, "act": 0.15},
    "h_time_curve": 1.0,
    "h_counterfactual_cost": 14.8,
    "defense_in_depth": [{"index": 0, "failure_mode": "sensor_failure", "coverage": 0.33}],
}


def test_has_context_and_type():
    d = to_jsonld(SAMPLE)
    assert "@context" in d
    assert d["@type"] == "OversightAssessment"


def test_h_quantity_roundtrips():
    assert "70.35" in json.dumps(to_jsonld(SAMPLE))


def test_str_is_valid_json_equal_to_dict():
    s = to_jsonld_str(SAMPLE)
    assert isinstance(s, str)
    assert json.loads(s) == to_jsonld(SAMPLE)
