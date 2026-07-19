import pytest
from chof_calc.backtest_incidents import INCIDENTS, backtest_h, run_all

ELEMS = {"RR", "CC", "EE", "TT", "SS", "AA", "II"}
NAMES = {
    "iran_air_655_1988",
    "kargu_2_libya_2020",
    "therac_25_1980s",
    "boeing_737_max_2018_2019",
}


def test_four_incidents():
    assert set(INCIDENTS) == NAMES


@pytest.mark.parametrize("name", sorted(NAMES))
def test_fixtures_well_formed(name):
    fx = INCIDENTS[name]
    assert set(fx["scores"]) == ELEMS
    assert set(fx["weights"]) == ELEMS
    assert all(1 <= v <= 45 for v in fx["scores"].values())
    assert all(w > 0 for w in fx["weights"].values())
    assert isinstance(fx["note"], str) and fx["note"]


@pytest.mark.parametrize("name", sorted(NAMES))
def test_h_non_absurd(name):
    assert 0.0 <= backtest_h(name) <= 100.0


def test_run_all():
    r = run_all()
    assert set(r) == NAMES
    assert all(0.0 <= v <= 100.0 for v in r.values())


def test_unknown_incident_raises():
    with pytest.raises(KeyError):
        backtest_h("nope")
