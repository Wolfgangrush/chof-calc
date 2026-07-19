"""
Tests for the pure-function H equation and its validators.
"""

import pytest

from chof_calc.elements import Elements, RiskBand
from chof_calc.equation import HEquation, OversightSeverity
from chof_calc.transparency import TransparencyClass
from chof_calc.weights import Weights


def _equal_weights() -> Weights:
    """Seven equal weights = 1/7 each, sum = 1."""
    w = 1.0 / 7.0
    return Weights(W_RR=w, W_CC=w, W_EE=w, W_TT=w, W_SS=w, W_AA=w, W_II=w)


def test_h_at_minimum_score_returns_near_100():
    """All elements at minimum (score=1) -> high H (near 99)."""
    elements = Elements(RR=1, CC=1, EE=1, TT=1, SS=1, AA=1, II=1)
    weights = _equal_weights()
    result = HEquation.compute(elements, weights)
    assert abs(result.h_quantity - 99.0) < 0.01


def test_h_at_maximum_score_returns_55():
    """All elements at maximum (score=45) -> H = 100 - 45 = 55."""
    elements = Elements(RR=45, CC=45, EE=45, TT=45, SS=45, AA=45, II=45)
    weights = _equal_weights()
    result = HEquation.compute(elements, weights)
    assert abs(result.h_quantity - 55.0) < 0.01


def test_h_at_midpoint_is_intermediate():
    """All elements at midpoint (score=23) -> H = 100 - 23 = 77."""
    elements = Elements(RR=23, CC=23, EE=23, TT=23, SS=23, AA=23, II=23)
    weights = _equal_weights()
    result = HEquation.compute(elements, weights)
    assert abs(result.h_quantity - 77.0) < 0.01


def test_weights_must_sum_to_one():
    """Weights summing to anything other than 1.0 must raise."""
    with pytest.raises(ValueError, match="must sum to 1.0"):
        Weights(
            W_RR=0.5,
            W_CC=0.5,
            W_EE=0.5,
            W_TT=0.5,
            W_SS=0.5,
            W_AA=0.5,
            W_II=0.5,
        )


def test_weights_must_be_in_range():
    """Weights outside [0, 1] must raise."""
    with pytest.raises(ValueError, match="outside the valid range"):
        Weights(
            W_RR=-0.1,
            W_CC=0.18,
            W_EE=0.18,
            W_TT=0.18,
            W_SS=0.18,
            W_AA=0.18,
            W_II=0.20,
        )


def test_element_scores_must_be_in_band():
    """Element scores outside [1, 45] must raise."""
    with pytest.raises(ValueError, match="outside the valid score band"):
        Elements(RR=0, CC=20, EE=20, TT=20, SS=20, AA=20, II=20)
    with pytest.raises(ValueError, match="outside the valid score band"):
        Elements(RR=46, CC=20, EE=20, TT=20, SS=20, AA=20, II=20)


def test_risk_band_classification():
    """Risk-band thresholds per dissertation Table 4.1."""
    assert RiskBand.from_score(1) == RiskBand.LOW
    assert RiskBand.from_score(15) == RiskBand.LOW
    assert RiskBand.from_score(16) == RiskBand.MEDIUM
    assert RiskBand.from_score(30) == RiskBand.MEDIUM
    assert RiskBand.from_score(31) == RiskBand.HIGH
    assert RiskBand.from_score(45) == RiskBand.HIGH


def test_oversight_severity_classification():
    """Severity bands for traffic-light coding."""
    assert OversightSeverity.from_h(20) == OversightSeverity.LOW
    assert OversightSeverity.from_h(50) == OversightSeverity.MEDIUM
    assert OversightSeverity.from_h(75) == OversightSeverity.HIGH
    assert OversightSeverity.from_h(95) == OversightSeverity.CRITICAL


def test_computation_trace_is_human_readable():
    """The computation trace should be a non-empty list of strings that
    walks through the equation step by step (for CLI + web app display).
    """
    elements = Elements(RR=10, CC=10, EE=10, TT=10, SS=10, AA=10, II=10)
    weights = _equal_weights()
    result = HEquation.compute(elements, weights)
    assert isinstance(result.computation_trace, list)
    assert len(result.computation_trace) >= 4
    # Final line should contain the answer.
    assert "%" in result.computation_trace[-1]
    assert "H = " in result.computation_trace[-1]


def test_result_as_dict_round_trips():
    """HResult.as_dict() should produce a JSON-serialisable structure."""
    import json

    elements = Elements(RR=10, CC=10, EE=10, TT=10, SS=10, AA=10, II=10)
    weights = _equal_weights()
    result = HEquation.compute(elements, weights, TransparencyClass.BLACK_BOX)
    serialised = json.dumps(result.as_dict())
    parsed = json.loads(serialised)
    assert abs(parsed["h_quantity"] - result.h_quantity) < 0.001
    assert parsed["transparency_class"] == "black_box"
