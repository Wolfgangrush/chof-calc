"""Monte-Carlo sensitivity analysis of the Human-Oversight score H."""
from __future__ import annotations

import random
import statistics


def h_score(scores: dict[str, float], weights: dict[str, float]) -> float:
    """Compute the Human-Oversight score H.

    H = 100 - sum(weights[k] * scores[k] for k) / sum(weights.values())

    Parameters
    ----------
    scores : dict[str, float]
        Element scores keyed by element name.
    weights : dict[str, float]
        Weights keyed by element name. Must share keys with ``scores`` and
        have a strictly positive sum.

    Returns
    -------
    float
        The Human-Oversight score H.

    Raises
    ------
    ValueError
        If ``scores`` and ``weights`` have different keys, or
        ``sum(weights.values())`` is not strictly positive.
    """
    if set(scores.keys()) != set(weights.keys()):
        raise ValueError("scores and weights must have the same keys")
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("sum(weights.values()) must be > 0")
    weighted_sum = sum(weights[k] * scores[k] for k in scores)
    return 100.0 - weighted_sum / total_weight


def _percentile(sorted_data: list[float], p: float) -> float:
    """Linear-interpolation percentile on a pre-sorted list (p in [0, 100])."""
    n = len(sorted_data)
    if n == 0:
        raise ValueError("cannot compute percentile of empty data")
    if n == 1:
        return sorted_data[0]
    rank = (p / 100.0) * (n - 1)
    lo = int(rank)
    hi = min(lo + 1, n - 1)
    frac = rank - lo
    return sorted_data[lo] * (1.0 - frac) + sorted_data[hi] * frac


def monte_carlo(
    scores: dict[str, float],
    weights: dict[str, float],
    n: int = 2000,
    sigma: float = 2.0,
    seed: int = 0,
    score_min: float = 1.0,
    score_max: float = 45.0,
) -> dict:
    """Monte-Carlo sensitivity of the Human-Oversight score H.

    Runs ``n`` trials. In each trial every score is perturbed by Gaussian
    noise (mean 0, std ``sigma``) drawn from a single ``random.Random(seed)``
    instance, clamped to ``[score_min, score_max]``, and the resulting H is
    collected.

    Parameters
    ----------
    scores : dict[str, float]
        Element scores keyed by element name.
    weights : dict[str, float]
        Weights keyed by element name; same keys as ``scores``, sum > 0.
    n : int
        Number of trials (>= 1).
    sigma : float
        Standard deviation of the Gaussian noise (>= 0).
    seed : int
        Seed for the deterministic ``random.Random`` instance.
    score_min : float
        Lower clamp for perturbed scores.
    score_max : float
        Upper clamp for perturbed scores.

    Returns
    -------
    dict
        ``{"mean": float, "std": float, "p05": float, "p50": float,
        "p95": float, "n": int}`` where p05/p50/p95 are the
        5th/50th/95th percentiles of the H samples.

    Raises
    ------
    ValueError
        If ``n < 1``, ``sigma < 0``, or the scores/weights are invalid
        per :func:`h_score`.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if sigma < 0:
        raise ValueError("sigma must be >= 0")
    if set(scores.keys()) != set(weights.keys()):
        raise ValueError("scores and weights must have the same keys")
    if sum(weights.values()) <= 0:
        raise ValueError("sum(weights.values()) must be > 0")

    rng = random.Random(seed)
    keys = list(scores.keys())
    h_values: list[float] = []
    for _ in range(n):
        perturbed = {
            k: max(score_min, min(score_max, scores[k] + rng.gauss(0.0, sigma)))
            for k in keys
        }
        h_values.append(h_score(perturbed, weights))

    h_sorted = sorted(h_values)
    mean = statistics.fmean(h_values)
    std = statistics.pstdev(h_values) if n > 1 else 0.0
    return {
        "mean": mean,
        "std": std,
        "p05": _percentile(h_sorted, 5),
        "p50": _percentile(h_sorted, 50),
        "p95": _percentile(h_sorted, 95),
        "n": n,
    }
