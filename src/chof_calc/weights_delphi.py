from __future__ import annotations

import statistics


def _percentile(sorted_data: list[float], p: float) -> float:
    """Return the ``p``-th percentile (0 <= p <= 1) of already-sorted data.

    Uses linear interpolation between adjacent order statistics (the
    inclusive / R type 7 method). Single-element lists return that single
    value so that q1/q3 collapse to the lone value, yielding iqr == 0.
    """
    n = len(sorted_data)
    if n == 0:
        raise ValueError("data must be non-empty")
    if n == 1:
        return sorted_data[0]
    rank = p * (n - 1)
    lower = int(rank)
    upper = min(lower + 1, n - 1)
    frac = rank - lower
    return sorted_data[lower] + frac * (sorted_data[upper] - sorted_data[lower])


def panel_stats(estimates: list[float]) -> dict:
    """Summarize a single round of panelist estimates.

    Args:
        estimates: Non-empty list of numeric expert estimates for one round.

    Returns:
        Dictionary with keys ``median``, ``q1``, ``q3``, ``iqr``, ``n`` where
        ``q1`` / ``q3`` are the 25th / 75th percentiles (inclusive method)
        and ``iqr`` = ``q3`` - ``q1``.

    Raises:
        ValueError: If ``estimates`` is empty.
    """
    if not estimates:
        raise ValueError("estimates must be a non-empty list")

    sorted_vals = sorted(estimates)
    q1 = _percentile(sorted_vals, 0.25)
    q3 = _percentile(sorted_vals, 0.75)
    return {
        "median": statistics.median(estimates),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "n": len(estimates),
    }


def delphi_aggregate(
    rounds: list[list[float]],
    iqr_threshold: float = 5.0,
) -> dict:
    """Aggregate successive rounds of a Delphi-method expert elicitation.

    Each round is a list of panelist estimates for the same quantity. Later
    rounds represent re-estimations after feedback, moving toward consensus.
    The function reports the median and IQR of the *last* round, whether
    that last round meets the consensus threshold, and the index of the
    first round that ever did.

    Args:
        rounds: Non-empty list of non-empty rounds (list of estimates per
            round). Length must be >= 1 and every inner list must be
            non-empty.
        iqr_threshold: Maximum IQR that qualifies as consensus. Defaults
            to 5.0 (appropriate for a 0-100 scoring scale).

    Returns:
        Dictionary with keys ``final_median``, ``final_iqr``, ``consensus``,
        and ``converged_round``. ``consensus`` is True iff the final round's
        IQR is <= ``iqr_threshold``. ``converged_round`` is the 0-based
        index of the first round whose IQR is <= ``iqr_threshold``, or -1
        if no round ever reached the threshold.

    Raises:
        ValueError: If ``rounds`` is empty, or any individual round is
            empty.
    """
    if not rounds:
        raise ValueError("rounds must be a non-empty list")
    for r in rounds:
        if not r:
            raise ValueError("each round must be a non-empty list")

    last_stats = panel_stats(rounds[-1])
    final_median = last_stats["median"]
    final_iqr = last_stats["iqr"]

    converged_round = -1
    for idx, r in enumerate(rounds):
        if panel_stats(r)["iqr"] <= iqr_threshold:
            converged_round = idx
            break

    return {
        "final_median": final_median,
        "final_iqr": final_iqr,
        "consensus": final_iqr <= iqr_threshold,
        "converged_round": converged_round,
    }
