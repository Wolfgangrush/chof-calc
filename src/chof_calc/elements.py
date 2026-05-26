"""
The seven CHOF elements + scoring-band scaffolding.

Per Mahajan (2024) Table 4.1 — Human Oversight Risk Assessment Elements
and Weight Distribution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Element(str, Enum):
    """The seven elements of the H equation."""

    RR = "RR"  # Risk Level
    CC = "CC"  # Operational Complexity
    EE = "EE"  # Ethical & Legal Compliance
    TT = "TT"  # Technological Reliability
    SS = "SS"  # Safety Concerns
    AA = "AA"  # Accuracy of Targeting
    II = "II"  # Accountability Issues


ELEMENT_LABELS: dict[Element, str] = {
    Element.RR: "Risk Level",
    Element.CC: "Operational Complexity",
    Element.EE: "Ethical & Legal Compliance",
    Element.TT: "Technological Reliability",
    Element.SS: "Safety Concerns",
    Element.AA: "Accuracy of Targeting",
    Element.II: "Accountability Issues",
}

ELEMENT_DESCRIPTIONS: dict[Element, str] = {
    Element.RR: (
        "Risk Level. Captures the potential for unintended civilian "
        "casualties and other severe consequences. Higher in combat "
        "environments with civilian presence."
    ),
    Element.CC: (
        "Operational Complexity. Captures challenges of managing AWS "
        "deployment in dynamic and unpredictable environments."
    ),
    Element.EE: (
        "Ethical & Legal Compliance. Captures alignment with International "
        "Humanitarian Law (distinction, proportionality, necessity) and "
        "ethical principles."
    ),
    Element.TT: (
        "Technological Reliability. Captures predictability of system "
        "behaviour, robustness to environmental variation, malfunction rate."
    ),
    Element.SS: (
        "Safety Concerns. Captures potential risks to human life and "
        "operational safety protocols beyond technical reliability."
    ),
    Element.AA: (
        "Accuracy of Targeting. Captures the system's ability to correctly "
        "identify and engage intended targets."
    ),
    Element.II: (
        "Accountability Issues. Captures how clearly responsibility can be "
        "traced when the system causes harm; the 'moral crumple zone' risk."
    ),
}

# Score band [1, 45] — split into Low / Medium / High per dissertation Table 4.1.
SCORE_MIN = 1
SCORE_MAX = 45


class RiskBand(str, Enum):
    """Risk band classification per dissertation scoring rubric."""

    LOW = "low"  # [1, 15]
    MEDIUM = "medium"  # [16, 30]
    HIGH = "high"  # [31, 45]

    @classmethod
    def from_score(cls, score: float) -> "RiskBand":
        """Classify a score (1-45) into its risk band."""
        if not (SCORE_MIN <= score <= SCORE_MAX):
            raise ValueError(
                f"Score must be in [{SCORE_MIN}, {SCORE_MAX}]; got {score}."
            )
        if score <= 15:
            return cls.LOW
        if score <= 30:
            return cls.MEDIUM
        return cls.HIGH


@dataclass(frozen=True)
class Elements:
    """The seven element scores for a weapon system.

    Each score is on the [1, 45] band per Mahajan (2024) Table 4.1.
    Low risk = [1, 15] · Medium risk = [16, 30] · High risk = [31, 45].
    """

    RR: float  # Risk Level
    CC: float  # Operational Complexity
    EE: float  # Ethical & Legal Compliance
    TT: float  # Technological Reliability
    SS: float  # Safety Concerns
    AA: float  # Accuracy of Targeting
    II: float  # Accountability Issues

    def __post_init__(self) -> None:
        for name in ("RR", "CC", "EE", "TT", "SS", "AA", "II"):
            value = getattr(self, name)
            if not (SCORE_MIN <= value <= SCORE_MAX):
                raise ValueError(
                    f"Element {name} = {value} is outside the valid score "
                    f"band [{SCORE_MIN}, {SCORE_MAX}]."
                )

    def as_dict(self) -> dict[Element, float]:
        """Return as a dictionary keyed by Element enum."""
        return {
            Element.RR: self.RR,
            Element.CC: self.CC,
            Element.EE: self.EE,
            Element.TT: self.TT,
            Element.SS: self.SS,
            Element.AA: self.AA,
            Element.II: self.II,
        }

    def risk_bands(self) -> dict[Element, RiskBand]:
        """Return the risk band for each element."""
        return {el: RiskBand.from_score(score) for el, score in self.as_dict().items()}
