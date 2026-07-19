import pytest
from chof_calc.sensitivity_monte_carlo import h_score, monte_carlo as mc

S = {"RR": 35, "CC": 30, "EE": 28}
Wt = {"RR": 0.4, "CC": 0.35, "EE": 0.25}


def test_h_score_value():
    assert h_score(S, Wt) == pytest.approx(68.5)


def test_sigma_zero_is_exact():
    r = mc(S, Wt, n=300, sigma=0.0, seed=1)
    assert r["mean"] == pytest.approx(h_score(S, Wt))
    assert r["std"] == 0.0


def test_determinism_same_seed():
    assert mc(S, Wt, n=300, sigma=3.0, seed=7) == mc(S, Wt, n=300, sigma=3.0, seed=7)


def test_percentiles_ordered():
    r = mc(S, Wt, n=500, sigma=3.0, seed=2)
    assert r["p05"] <= r["p50"] <= r["p95"]


def test_larger_sigma_larger_std():
    hi = mc(S, Wt, n=800, sigma=5.0, seed=3)["std"]
    lo = mc(S, Wt, n=800, sigma=1.0, seed=3)["std"]
    assert hi > lo


@pytest.mark.parametrize("kw", [dict(n=0), dict(sigma=-1)])
def test_invalid_raises(kw):
    with pytest.raises(ValueError):
        mc(S, Wt, **kw)


def test_h_score_key_mismatch_raises():
    with pytest.raises(ValueError):
        h_score({"RR": 1}, {"CC": 1})
