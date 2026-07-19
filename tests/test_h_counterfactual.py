import pytest
from chof_calc.h_counterfactual import counterfactual_cost as cc, marginal_cost_per_point as mc


def test_full_oversight_zero_cost():
    for e in (0.0, 0.3, 1.0):
        assert cc(100, e) == pytest.approx(0.0)


def test_zero_oversight_full_exposure():
    assert cc(0, 1.0, 100) == pytest.approx(100.0)


def test_known_value():
    assert cc(75, 0.5, 100) == pytest.approx(12.5)


def test_monotone_nonincreasing_in_h():
    vals = [cc(h, 0.8, 100) for h in (0, 25, 50, 75, 100)]
    assert all(vals[i] >= vals[i + 1] - 1e-9 for i in range(len(vals) - 1))


def test_marginal_cost_per_point():
    assert mc(1.0, 100) == pytest.approx(1.0)
    assert mc(0.5, 100) == pytest.approx(0.5)


@pytest.mark.parametrize("args", [(150, 0.5), (50, 1.5), (50, 0.5, -1)])
def test_invalid_raises(args):
    with pytest.raises(ValueError):
        cc(*args)
