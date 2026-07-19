"""Historical incident backtest harness for the Human-Oversight score (CHOF).

The CHOF model has seven oversight elements — RR, CC, EE, TT, SS, AA, II —
each scored on [1, 45] where higher means worse performance on that element.
The Human-Oversight score is::

    H = 100 - sum(weights[k] * scores[k]) / sum(weights.values())

This module ships four curated fixtures of real-world incidents where
automation-trust or oversight-architecture failures caused documented harm.
Each fixture records per-element scores, per-element positive weights, and
a one-line rationale. Use :func:`backtest_h` to score one incident or
:func:`run_all` to score all four.
"""

from __future__ import annotations

from typing import Dict, Mapping

ELEMENTS: tuple[str, ...] = ("RR", "CC", "EE", "TT", "SS", "AA", "II")

INCIDENTS: Dict[str, Dict[str, object]] = {
    "iran_air_655_1988": {
        "scores": {"RR": 38, "CC": 32, "EE": 35, "TT": 28, "SS": 30, "AA": 22, "II": 42},
        "weights": {"RR": 1.0, "CC": 1.5, "EE": 1.0, "TT": 1.0, "SS": 1.0, "AA": 1.0, "II": 2.0},
        "note": (
            "USS Vincennes misidentified Iran Air 655 as an F-14; identification "
            "and command-and-control failures dominated a tense combat identification."
        ),
    },
    "kargu_2_libya_2020": {
        "scores": {"RR": 35, "CC": 38, "EE": 40, "TT": 32, "SS": 35, "AA": 36, "II": 30},
        "weights": {"RR": 1.0, "CC": 1.5, "EE": 2.0, "TT": 1.0, "SS": 1.0, "AA": 1.5, "II": 1.0},
        "note": (
            "Alleged first autonomous lethal engagement by a loitering munition; "
            "engagement-rule and accountability gaps are central to the failure mode."
        ),
    },
    "therac_25_1980s": {
        "scores": {"RR": 25, "CC": 30, "EE": 22, "TT": 20, "SS": 45, "AA": 38, "II": 28},
        "weights": {"RR": 1.0, "CC": 1.0, "EE": 1.0, "TT": 1.0, "SS": 2.0, "AA": 1.5, "II": 1.0},
        "note": (
            "Software race condition disabled hardware interlocks on a radiotherapy "
            "machine; safety systems and corporate accountability collapsed together."
        ),
    },
    "boeing_737_max_2018_2019": {
        "scores": {"RR": 36, "CC": 32, "EE": 28, "TT": 35, "SS": 42, "AA": 40, "II": 30},
        "weights": {"RR": 1.0, "CC": 1.0, "EE": 1.0, "TT": 1.0, "SS": 1.5, "AA": 2.0, "II": 1.0},
        "note": (
            "MCAS single-sensor architecture with FAA-delegated certification; "
            "safety architecture and oversight accountability both failed."
        ),
    },
}


def backtest_h(incident_name: str) -> float:
    """Compute the Human-Oversight score ``H`` for a named historical incident.

    Args:
        incident_name: Key in :data:`INCIDENTS`.

    Returns:
        The score ``H`` as a ``float`` in [0, 100]. Larger means better
        human-oversight posture; smaller means worse.

    Raises:
        KeyError: If ``incident_name`` is not a fixture in :data:`INCIDENTS`.
    """
    fixture = INCIDENTS[incident_name]
    scores: Mapping[str, float] = fixture["scores"]  # type: ignore[assignment]
    weights: Mapping[str, float] = fixture["weights"]  # type: ignore[assignment]
    numerator = sum(weights[k] * scores[k] for k in ELEMENTS)
    denominator = sum(weights[k] for k in ELEMENTS)
    return 100.0 - numerator / denominator


def run_all() -> Dict[str, float]:
    """Return ``{incident_name: H}`` for every fixture in :data:`INCIDENTS`."""
    return {name: backtest_h(name) for name in INCIDENTS}
