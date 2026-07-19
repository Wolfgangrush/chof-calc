"""One-at-a-time (tornado) sensitivity analysis for the Human-Oversight score H.

The Human-Oversight score H is defined locally as

    H = 100 - sum(weights[k] * scores[k]) / sum(weights.values())

This module exposes :func:`tornado` which performs a one-at-a-time sensitivity
analysis: for every element, the score is perturbed down by ``delta`` and up
by ``delta`` (each clamped to ``[score_min, score_max]``) while every other
element is held fixed. The Human-Oversight score is recomputed at the low and
high settings and the swing ``abs(high_H - low_H)`` is recorded. The result is
returned sorted by swing, descending, so the most influential elements appear
first.
"""
from __future__ import annotations


def _compute_h(scores: dict[str, float], weights: dict[str, float]) -> float:
    """Replicate the Human-Oversight score formula.

    H = 100 - sum(weights[k] * scores[k]) / sum(weights.values())
    """
    total_weight = sum(weights.values())
    weighted_sum = 0.0
    for key in weights:
        weighted_sum += weights[key] * scores[key]
    return 100.0 - weighted_sum / total_weight


def tornado(
    scores: dict[str, float],
    weights: dict[str, float],
    delta: float = 5.0,
    score_min: float = 1.0,
    score_max: float = 45.0,
) -> list[dict]:
    """Compute a tornado sensitivity for the Human-Oversight score H.

    For each element, hold the remaining scores fixed and move that single
    score down by ``delta`` and up by ``delta`` (each clamped to
    ``[score_min, score_max]``). The Human-Oversight score H is recomputed at
    the low and high settings and the swing is ``abs(high_H - low_H)``.

    Parameters
    ----------
    scores : dict[str, float]
        Current score for every element.
    weights : dict[str, float]
        Weight for every element. Must contain the same set of keys as
        ``scores``.
    delta : float, default 5.0
        Magnitude of the score movement applied in each direction. Must be
        greater than or equal to zero.
    score_min : float, default 1.0
        Lower clamp applied to the perturbed score.
    score_max : float, default 45.0
        Upper clamp applied to the perturbed score.

    Returns
    -------
    list[dict]
        One entry per element with keys ``"element"``, ``"low_H"``, ``"high_H"``
        and ``"swing"``. Sorted by ``"swing"`` descending.

    Raises
    ------
    ValueError
        If ``scores`` and ``weights`` do not contain the same keys, the total
        weight is not strictly positive, or ``delta`` is negative.
    """
    if set(scores) != set(weights):
        raise ValueError("scores and weights must share the same keys")
    total_weight = sum(weights.values())
    if total_weight <= 0.0:
        raise ValueError("sum of weights must be > 0")
    if delta < 0.0:
        raise ValueError("delta must be >= 0")

    rows: list[dict] = []
    for key in scores:
        original = scores[key]
        low_score = max(score_min, original - delta)
        high_score = min(score_max, original + delta)

        low_scores = dict(scores)
        low_scores[key] = low_score
        high_scores = dict(scores)
        high_scores[key] = high_score

        low_H = _compute_h(low_scores, weights)
        high_H = _compute_h(high_scores, weights)
        swing = abs(high_H - low_H)

        rows.append(
            {
                "element": key,
                "low_H": low_H,
                "high_H": high_H,
                "swing": swing,
            }
        )

    rows.sort(key=lambda row: row["swing"], reverse=True)
    return rows
