import pytest
from chof_calc.h_v2 import compute_h_v2, h_v2_for
from chof_calc.systems.fixtures import get_fixture, list_fixtures
from chof_calc.equation import HEquation


def test_full_vector_keys():
    r = h_v2_for("mq9")
    for k in (
        "system",
        "h_quantity",
        "severity",
        "transparency_class",
        "h_modality",
        "dominant_modality",
        "h_latency_profile",
        "h_time_curve",
        "h_counterfactual_cost",
        "defense_in_depth",
    ):
        assert k in r


def test_h_quantity_matches_equation():
    f = get_fixture("mq9")
    assert compute_h_v2(f)["h_quantity"] == pytest.approx(
        HEquation.compute(f.elements, f.weights, f.transparency).h_quantity
    )


def test_mq9_anchor_preserved():
    assert h_v2_for("mq9")["h_quantity"] == pytest.approx(70.35, abs=0.01)


def test_modality_and_latency_sum_to_one():
    r = h_v2_for("mq9", engagement_time_s=8)
    assert sum(r["h_modality"].values()) == pytest.approx(1.0)
    assert sum(r["h_latency_profile"].values()) == pytest.approx(1.0)


def test_counterfactual_scales_with_exposure():
    lo = h_v2_for("mq9", exposure=0.2)["h_counterfactual_cost"]
    hi = h_v2_for("mq9", exposure=0.9)["h_counterfactual_cost"]
    assert 0 <= lo <= hi


def test_defense_layers_count():
    assert len(h_v2_for("mq9", n_layers=4)["defense_in_depth"]) == 4


def test_deployment_phase_affects_time_curve():
    a = h_v2_for("mq9", deployment_phase="active")["h_time_curve"]
    p = h_v2_for("mq9", deployment_phase="post_deployment")["h_time_curve"]
    assert a > p


def test_all_fixtures_compute_non_absurd():
    for f in list_fixtures():
        r = compute_h_v2(f)
        assert 0.0 <= r["h_quantity"] <= 100.0
