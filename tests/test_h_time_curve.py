import pytest
from chof_calc.h_time_curve import (
    phase_oversight_multiplier as m,
    lifecycle_profile,
    weighted_oversight,
)


def test_exact_multipliers():
    assert m("pre_deployment") == pytest.approx(0.70)
    assert m("active") == pytest.approx(1.00)
    assert m("post_deployment") == pytest.approx(0.40)


def test_active_is_max():
    assert m("active") == max(lifecycle_profile().values())


def test_lifecycle_keys():
    assert set(lifecycle_profile()) == {"pre_deployment", "active", "post_deployment"}


def test_weighted_values():
    assert weighted_oversight(1.0, "active") == pytest.approx(1.0)
    assert weighted_oversight(0.8, "post_deployment") == pytest.approx(0.32)
    assert weighted_oversight(0.5, "pre_deployment") == pytest.approx(0.35)


def test_weighted_clamped_unit_interval():
    assert 0.0 <= weighted_oversight(1.0, "active") <= 1.0


@pytest.mark.parametrize("bad", ["", "live", "Active", None])
def test_invalid_phase_raises(bad):
    with pytest.raises((ValueError, TypeError)):
        m(bad)


@pytest.mark.parametrize("base", [-0.1, 1.5])
def test_invalid_base_raises(base):
    with pytest.raises(ValueError):
        weighted_oversight(base, "active")
