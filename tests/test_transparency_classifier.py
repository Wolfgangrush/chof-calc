import pytest
from chof_calc.transparency_classifier import classify_transparency as c, transparency_score as ts


def test_corners():
    assert c(1, 1, 1) == "white_box"
    assert c(0, 0, 0) == "black_box"
    assert c(0.5, 0.5, 0.5) == "glass_box"


def test_thresholds():
    assert c(0.67, 0.67, 0.67) == "white_box"
    assert c(0.34, 0.34, 0.34) == "glass_box"
    assert c(0.33, 0.33, 0.33) == "black_box"


def test_score_is_mean():
    assert ts(0.2, 0.4, 0.6) == pytest.approx(0.4)


@pytest.mark.parametrize("bad", [(1.2, 0, 0), (-0.1, 0.5, 0.5), (0.5, 0.5, 2.0)])
def test_out_of_range_raises(bad):
    with pytest.raises(ValueError):
        c(*bad)
