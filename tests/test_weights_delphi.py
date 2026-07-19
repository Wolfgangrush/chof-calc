import pytest
from chof_calc.weights_delphi import panel_stats as ps, delphi_aggregate as da


def test_all_equal_iqr_zero():
    assert ps([7, 7, 7, 7])["iqr"] == 0


def test_single_value():
    r = ps([5])
    assert r["median"] == 5 and r["iqr"] == 0 and r["n"] == 1


def test_converges_at_round():
    r = da([[1, 50], [10, 40], [24, 26]], iqr_threshold=5)
    assert r["converged_round"] == 2
    assert r["consensus"] is True
    assert r["final_median"] == 25


def test_never_converges():
    r = da([[1, 50], [2, 49]], iqr_threshold=5)
    assert r["converged_round"] == -1
    assert r["consensus"] is False


def test_final_median_is_last_round():
    r = da([[1, 2, 3], [10, 20, 30]], iqr_threshold=100)
    assert r["final_median"] == 20


def test_empty_raises():
    with pytest.raises(ValueError):
        ps([])
    with pytest.raises(ValueError):
        da([])
    with pytest.raises(ValueError):
        da([[]])
