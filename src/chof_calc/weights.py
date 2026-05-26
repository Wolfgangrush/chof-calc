"""
Weight elicitation + validation for the H equation.

Each of the seven elements has a weight W in [0, 1]. Weights must sum to 1.0
within a small tolerance.
"""

from __future__ import annotations

from dataclasses import dataclass

from chof_calc.elements import Element

WEIGHT_SUM_TOLERANCE = 1e-9


@dataclass(frozen=True)
class Weights:
    """Weights for the seven CHOF elements.

    Each weight is in [0, 1]; the sum must equal 1.0 within tolerance.
    """

    W_RR: float
    W_CC: float
    W_EE: float
    W_TT: float
    W_SS: float
    W_AA: float
    W_II: float

    def __post_init__(self) -> None:
        for name in ("W_RR", "W_CC", "W_EE", "W_TT", "W_SS", "W_AA", "W_II"):
            value = getattr(self, name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"Weight {name} = {value} is outside the valid range [0, 1]."
                )
        total = self.sum()
        if abs(total - 1.0) > WEIGHT_SUM_TOLERANCE:
            raise ValueError(
                f"Weights must sum to 1.0 (within tolerance "
                f"{WEIGHT_SUM_TOLERANCE}); got sum = {total}."
            )

    def sum(self) -> float:
        """Return the sum of all weights (used as the normaliser in H)."""
        return (
            self.W_RR
            + self.W_CC
            + self.W_EE
            + self.W_TT
            + self.W_SS
            + self.W_AA
            + self.W_II
        )

    def as_dict(self) -> dict[Element, float]:
        """Return as a dictionary keyed by Element enum."""
        return {
            Element.RR: self.W_RR,
            Element.CC: self.W_CC,
            Element.EE: self.W_EE,
            Element.TT: self.W_TT,
            Element.SS: self.W_SS,
            Element.AA: self.W_AA,
            Element.II: self.W_II,
        }
