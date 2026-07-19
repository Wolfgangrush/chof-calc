import pytest
from chof_calc.sensitivity_tornado import tornado

S = {"RR": 35, "CC": 30, "EE": 28, "TT": 20}
W = {"RR": 0.3, "CC": 0.3, "EE": 0.2, "TT": 0.2}


def test_one_entry_per_element():
    t = tornado(S, W, delta=5.0)
    assert len(t) == len(S)
    assert {x["element"] for x in t} == set(S)
    assert all(set(x) == {"element", "low_H", "high_H", "swing"} for x in t)


def test_sorted_descending_by_swing():
    t = tornado(S, W, delta=5.0)
    assert all(t[i]["swing"] >= t[i + 1]["swing"] - 1e-9 for i in range(len(t) - 1))


def test_swings_nonnegative():
    assert all(x["swing"] >= 0 for x in tornado(S, W, delta=5.0))


def test_zero_delta_zero_swing():
    assert all(abs(x["swing"]) < 1e-9 for x in tornado(S, W, delta=0.0))


def test_key_mismatch_raises():
    with pytest.raises(ValueError):
        tornado({"RR": 1}, {"CC": 1})


def test_negative_delta_raises():
    with pytest.raises(ValueError):
        tornado(S, W, delta=-1)
