"""
Gate 1 — MQ-9 regression anchor.

Per Mahajan (2024) Ch 4.6 Simulation pp.41-42:
  - Element scores: RR=35, CC=30, EE=28, TT=20, SS=25, AA=30, II=32
  - Weights: 0.25, 0.15, 0.15, 0.10, 0.10, 0.15, 0.10 (SUM = 1.00)
  - Weighted sum: 29.65
  - Dissertation reports: H = 75.35 % (p.42)
  - Mathematically correct: H = 100 - 29.65 = 70.35 %

The published value (75.35) on p.42 contains an apparent arithmetic typo
in the final subtraction step. The underlying weighted-sum 29.65 is
computed correctly in the dissertation.

This test verifies:
  (a) the tool reproduces the CORRECT mathematical answer (70.35 +- 0.01)
  (b) the tool emits a correction_note flagging the dissertation typo
  (c) the underlying weighted_sum (29.65) matches the dissertation exactly
"""

import pytest

from chof_calc.equation import HEquation
from chof_calc.systems import MQ9_REAPER


def test_mq9_weighted_sum_matches_dissertation():
    """The weighted-sum value (29.65) is correctly computed in the dissertation
    and the tool must reproduce it exactly within floating-point tolerance.
    """
    result = HEquation.compute(
        elements=MQ9_REAPER.elements,
        weights=MQ9_REAPER.weights,
        transparency=MQ9_REAPER.transparency,
        dissertation_published_value=MQ9_REAPER.dissertation_published_value,
    )
    assert abs(result.weighted_sum - 29.65) < 1e-9, (
        f"weighted_sum = {result.weighted_sum}, expected 29.65"
    )


def test_mq9_weight_total_is_one():
    """Dissertation weights sum to 1.00 exactly."""
    result = HEquation.compute(
        elements=MQ9_REAPER.elements,
        weights=MQ9_REAPER.weights,
    )
    assert abs(result.weight_total - 1.0) < 1e-9


def test_mq9_h_quantity_is_mathematically_correct():
    """H = 100 - 29.65 / 1.0 = 70.35 (NOT 75.35 as the dissertation prints
    on p.42 due to apparent arithmetic typo in final subtraction step).
    """
    result = HEquation.compute(
        elements=MQ9_REAPER.elements,
        weights=MQ9_REAPER.weights,
        transparency=MQ9_REAPER.transparency,
    )
    assert abs(result.h_quantity - 70.35) < 0.01, (
        f"H_quantity = {result.h_quantity}, expected 70.35 +- 0.01"
    )


def test_mq9_correction_note_fires_when_dissertation_value_passed():
    """When the dissertation's published value (75.35) is passed in,
    the result must carry a correction_note explaining the discrepancy.
    """
    result = HEquation.compute(
        elements=MQ9_REAPER.elements,
        weights=MQ9_REAPER.weights,
        transparency=MQ9_REAPER.transparency,
        dissertation_published_value=75.35,
    )
    assert result.correction_note is not None
    assert "75.35" in result.correction_note
    assert "70.35" in result.correction_note or "{:.2f}".format(result.h_quantity) in result.correction_note


def test_mq9_correction_note_silent_without_dissertation_value():
    """When no dissertation value is passed, no correction_note is emitted."""
    result = HEquation.compute(
        elements=MQ9_REAPER.elements,
        weights=MQ9_REAPER.weights,
        transparency=MQ9_REAPER.transparency,
    )
    assert result.correction_note is None


def test_mq9_per_element_contributions_match_dissertation():
    """Each of the seven per-element contributions on p.42:
      0.25 * 35 = 8.75
      0.15 * 30 = 4.50
      0.15 * 28 = 4.20
      0.10 * 20 = 2.00
      0.10 * 25 = 2.50
      0.15 * 30 = 4.50
      0.10 * 32 = 3.20
    """
    result = HEquation.compute(
        elements=MQ9_REAPER.elements,
        weights=MQ9_REAPER.weights,
    )
    contribs = result.element_contributions
    from chof_calc.elements import Element
    expected = {
        Element.RR: 8.75,
        Element.CC: 4.50,
        Element.EE: 4.20,
        Element.TT: 2.00,
        Element.SS: 2.50,
        Element.AA: 4.50,
        Element.II: 3.20,
    }
    for el, want in expected.items():
        got = contribs[el]
        assert abs(got - want) < 1e-9, (
            f"contribution[{el.value}] = {got}, expected {want}"
        )
