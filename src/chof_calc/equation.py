"""
The H equation — pure-function implementation.

Mahajan (2024) defines:

           1     N
  H = 100 - --- · Sigma (W_i * c_i)
          SUM_W  i=1

where i in {RR, CC, EE, TT, SS, AA, II}.

This module returns a structured HResult with all H_v2 outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from chof_calc.elements import Element, Elements, RiskBand
from chof_calc.transparency import TransparencyClass
from chof_calc.weights import Weights


class OversightSeverity(str, Enum):
    """Traffic-light severity classification for H_quantity."""

    LOW = "low"  # H < 40 — high autonomy permissible
    MEDIUM = "medium"  # 40 <= H < 70 — moderate oversight needed
    HIGH = "high"  # 70 <= H < 90 — high oversight needed
    CRITICAL = "critical"  # H >= 90 — near-total human control required

    @classmethod
    def from_h(cls, h: float) -> "OversightSeverity":
        if h < 40:
            return cls.LOW
        if h < 70:
            return cls.MEDIUM
        if h < 90:
            return cls.HIGH
        return cls.CRITICAL


@dataclass(frozen=True)
class HResult:
    """The structured H_v2 output.

    Includes the canonical scalar H_quantity (dissertation-faithful) plus
    H_v2 enrichment fields: transparency-class modality, severity band,
    per-element contribution breakdown, and the step-by-step computation
    trace that drives the live-math display in the web app.
    """

    h_quantity: float
    severity: OversightSeverity
    elements: Elements
    weights: Weights
    transparency: TransparencyClass
    weighted_sum: float
    weight_total: float
    element_contributions: dict[Element, float] = field(default_factory=dict)
    computation_trace: list[str] = field(default_factory=list)
    dissertation_published_value: float | None = None
    correction_note: str | None = None

    def as_dict(self) -> dict:
        return {
            "h_quantity": round(self.h_quantity, 4),
            "severity": self.severity.value,
            "elements": {el.value: score for el, score in self.elements.as_dict().items()},
            "weights": {el.value: w for el, w in self.weights.as_dict().items()},
            "transparency_class": self.transparency.value,
            "weighted_sum": round(self.weighted_sum, 4),
            "weight_total": round(self.weight_total, 4),
            "element_contributions": {
                el.value: round(v, 4) for el, v in self.element_contributions.items()
            },
            "computation_trace": self.computation_trace,
            "dissertation_published_value": self.dissertation_published_value,
            "correction_note": self.correction_note,
        }


class HEquation:
    """The H equation as a pure-function namespace."""

    @staticmethod
    def compute(
        elements: Elements,
        weights: Weights,
        transparency: TransparencyClass = TransparencyClass.GLASS_BOX,
        *,
        dissertation_published_value: float | None = None,
    ) -> HResult:
        """Compute the Human Oversight score.

        Args:
            elements: the seven element scores
            weights: the seven element weights (must sum to 1)
            transparency: the system's transparency class
                          (black box / glass box / white box)
            dissertation_published_value: optional. If set, the result will
                          carry a correction_note if the computed value
                          disagrees with the published value (used to flag
                          the apparent arithmetic typo on Mahajan 2024 p.42).

        Returns:
            HResult with all H_v2 outputs.
        """
        elem_dict = elements.as_dict()
        wt_dict = weights.as_dict()

        contributions: dict[Element, float] = {
            el: wt_dict[el] * elem_dict[el] for el in Element
        }
        weighted_sum = sum(contributions.values())
        weight_total = weights.sum()

        h_quantity = 100.0 - (weighted_sum / weight_total)
        severity = OversightSeverity.from_h(h_quantity)

        # Build the live-math computation trace (for CLI + web app display).
        terms = " + ".join(
            f"({wt_dict[el]:g} * {elem_dict[el]:g})" for el in Element
        )
        terms_values = " + ".join(
            f"{contributions[el]:.2f}" for el in Element
        )
        computation_trace = [
            f"H = 100 - [ {terms} ] / {weight_total:g}",
            f"H = 100 - [ {terms_values} ] / {weight_total:g}",
            f"H = 100 - {weighted_sum:.2f} / {weight_total:g}",
            f"H = 100 - {weighted_sum / weight_total:.4f}",
            f"H = {h_quantity:.4f} %",
        ]

        correction_note: str | None = None
        if dissertation_published_value is not None:
            diff = abs(h_quantity - dissertation_published_value)
            if diff > 0.01:
                correction_note = (
                    f"Note: the dissertation reports H = {dissertation_published_value:.2f}% "
                    f"for this system. The computed value is H = {h_quantity:.2f}%, "
                    f"a difference of {diff:.2f} percentage points. The underlying "
                    f"weighted-sum value ({weighted_sum:.2f}) is computed correctly in the "
                    f"dissertation; the apparent discrepancy is in the final "
                    f"subtraction step (100 - {weighted_sum:.2f} = {h_quantity:.2f}, "
                    f"not {dissertation_published_value:.2f}). The tool reports the "
                    f"mathematically correct value. See README section "
                    f"'Documented Corrections to the Published Dissertation'."
                )

        return HResult(
            h_quantity=h_quantity,
            severity=severity,
            elements=elements,
            weights=weights,
            transparency=transparency,
            weighted_sum=weighted_sum,
            weight_total=weight_total,
            element_contributions=contributions,
            computation_trace=computation_trace,
            dissertation_published_value=dissertation_published_value,
            correction_note=correction_note,
        )
