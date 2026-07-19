import pytest
from chof_calc.h_modality import oversight_modality, dominant_modality

EXPECT = {
    "black_box": {
        "ex_ante_constraint": 0.10,
        "in_flight_supervision": 0.35,
        "ex_post_audit": 0.55,
    },
    "glass_box": {
        "ex_ante_constraint": 0.34,
        "in_flight_supervision": 0.33,
        "ex_post_audit": 0.33,
    },
    "white_box": {
        "ex_ante_constraint": 0.55,
        "in_flight_supervision": 0.30,
        "ex_post_audit": 0.15,
    },
}


@pytest.mark.parametrize("tc,exp", EXPECT.items())
def test_exact_vectors(tc, exp):
    got = oversight_modality(tc)
    assert set(got) == set(exp)
    for k, v in exp.items():
        assert got[k] == pytest.approx(v)


@pytest.mark.parametrize("tc", EXPECT)
def test_sums_to_one(tc):
    assert sum(oversight_modality(tc).values()) == pytest.approx(1.0)


def test_black_box_leans_expost():
    assert dominant_modality("black_box") == "ex_post_audit"


def test_white_box_leans_exante():
    assert dominant_modality("white_box") == "ex_ante_constraint"


@pytest.mark.parametrize("bad", ["teal_box", "", "BLACK_BOX", None])
def test_invalid_raises(bad):
    with pytest.raises((ValueError, TypeError)):
        oversight_modality(bad)
