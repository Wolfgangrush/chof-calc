import pytest
from chof_calc.ooda_phase_mapper import latency_profile, feasible_phases

KEYS = {"observe", "orient", "decide", "act"}


@pytest.mark.parametrize("t", [0.5, 1, 5, 30, 60, 120, 600])
def test_sums_to_one_and_bounded(t):
    p = latency_profile(t)
    assert set(p) == KEYS
    assert sum(p.values()) == pytest.approx(1.0)
    assert all(0.0 <= v <= 1.0 for v in p.values())


def test_act_share_collapses_as_time_shrinks():
    assert latency_profile(1.0)["act"] < latency_profile(60.0)["act"]
    assert latency_profile(5)["act"] <= latency_profile(30)["act"] + 1e-9
    assert latency_profile(30)["act"] <= latency_profile(60)["act"] + 1e-9


def test_long_engagement_roughly_uniform():
    p = latency_profile(120.0)
    assert p["act"] == pytest.approx(0.25, abs=0.03)


def test_feasible_phases_filters_by_threshold():
    assert "act" in feasible_phases(120.0)
    assert "act" not in feasible_phases(0.5, threshold=0.1)


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_invalid_time_raises(bad):
    with pytest.raises(ValueError):
        latency_profile(bad)
