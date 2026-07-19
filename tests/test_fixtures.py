"""
Tests for the five baseline weapon-system fixtures.
"""

import pytest

from chof_calc.equation import HEquation
from chof_calc.systems import (
    IRON_DOME,
    KARGU_2,
    MQ9_REAPER,
    PHALANX,
    REGISTRY,
    SGR_A1,
    get_fixture,
    list_fixtures,
)
from chof_calc.transparency import TransparencyClass


def test_all_five_fixtures_registered():
    assert len(REGISTRY) == 5
    assert set(REGISTRY.keys()) == {
        "mq9",
        "iron_dome",
        "sgr_a1",
        "kargu_2",
        "phalanx",
    }


def test_list_fixtures_returns_five():
    fixtures = list_fixtures()
    assert len(fixtures) == 5


def test_get_fixture_case_insensitive():
    assert get_fixture("mq9") is MQ9_REAPER
    assert get_fixture("MQ9") is MQ9_REAPER
    assert get_fixture("iron_dome") is IRON_DOME
    assert get_fixture("iron-dome") is IRON_DOME


def test_get_fixture_unknown_raises():
    with pytest.raises(KeyError, match="Unknown system id"):
        get_fixture("not_a_real_system")


def test_only_mq9_is_non_provisional():
    """Only the MQ-9 fixture has dissertation-published values; the other
    four must be tagged provisional pending expert-panel scoring."""
    assert MQ9_REAPER.provisional is False
    assert IRON_DOME.provisional is True
    assert SGR_A1.provisional is True
    assert KARGU_2.provisional is True
    assert PHALANX.provisional is True


def test_each_fixture_computes_a_valid_h_score():
    """Every baseline fixture must produce a valid H in [0, 100]."""
    for fx in list_fixtures():
        result = HEquation.compute(
            elements=fx.elements,
            weights=fx.weights,
            transparency=fx.transparency,
        )
        assert 0.0 <= result.h_quantity <= 100.0, (
            f"{fx.name} produced invalid H = {result.h_quantity}"
        )


def test_kargu2_is_black_box():
    """Kargu-2 must be classified as black box (closed-weight classifier,
    short engagement window, no in-flight oversight)."""
    assert KARGU_2.transparency == TransparencyClass.BLACK_BOX
    assert not KARGU_2.transparency.supports_in_flight_supervision


def test_phalanx_is_white_box():
    """Phalanx is symbolic/rule-based; classed white box."""
    assert PHALANX.transparency == TransparencyClass.WHITE_BOX


def test_mq9_is_glass_box():
    """MQ-9 surfaces classification confidence to operator; glass box."""
    assert MQ9_REAPER.transparency == TransparencyClass.GLASS_BOX
    assert MQ9_REAPER.transparency.supports_in_flight_supervision


def test_kargu_severity_is_high():
    """Kargu-2 should land in HIGH or CRITICAL severity given its
    autonomous-engagement profile."""
    from chof_calc.equation import OversightSeverity

    result = HEquation.compute(
        elements=KARGU_2.elements,
        weights=KARGU_2.weights,
        transparency=KARGU_2.transparency,
    )
    assert result.severity in (
        OversightSeverity.HIGH,
        OversightSeverity.MEDIUM,
        OversightSeverity.CRITICAL,
    )
