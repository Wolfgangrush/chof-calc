"""Distribution of human-oversight attention across the Boyd OODA-loop phases.

This module models how an operator's finite attention budget should be split
across the Observe, Orient, Decide, and Act phases of an engagement, given
the available reaction time.

Public functions
----------------
latency_profile(engagement_time_s)
    Return a normalised budget distribution over the four phases.
feasible_phases(engagement_time_s, threshold=0.1)
    Return the phases whose budget share meets ``threshold``.
"""

from __future__ import annotations

__all__ = ["latency_profile", "feasible_phases"]

# Canonical ordering of the OODA-loop phase keys.
_PHASE_ORDER: tuple[str, ...] = ("observe", "orient", "decide", "act")


def latency_profile(engagement_time_s: float) -> dict[str, float]:
    """Return the per-phase attention budget for an engagement of ``engagement_time_s`` seconds.

    The model assumes that long engagements (``>= 60`` seconds) admit a roughly
    uniform budget across the four phases. As ``engagement_time_s`` shrinks
    toward zero, feasible late intervention collapses: the ``act`` share
    decreases monotonically toward ~0, and the freed mass is redistributed to
    ``observe`` (60%) and ``orient`` (40%).

    Parameters
    ----------
    engagement_time_s : float
        Available reaction time in seconds. Must be strictly positive.

    Returns
    -------
    dict[str, float]
        Mapping with exactly the keys ``"observe"``, ``"orient"``, ``"decide"``,
        ``"act"``. Each value lies in ``[0, 1]`` and the four values sum to
        ``1.0`` within floating-point tolerance.

    Raises
    ------
    ValueError
        If ``engagement_time_s`` is not strictly positive.
    """
    if engagement_time_s <= 0:
        raise ValueError(
            f"engagement_time_s must be > 0, got {engagement_time_s!r}"
        )

    # Saturation factor: 1.0 once engagement_time_s reaches 60s, linear below.
    f = min(1.0, engagement_time_s / 60.0)

    # Raw allocations per the model described in the module docstring.
    act_raw = 0.25 * f
    decide_raw = 0.25
    freed = 0.25 - act_raw
    observe_raw = 0.25 + 0.6 * freed
    orient_raw = 0.25 + 0.4 * freed

    raw = {
        "observe": observe_raw,
        "orient": orient_raw,
        "decide": decide_raw,
        "act": act_raw,
    }

    # Normalise so that the four shares sum to exactly 1.0.
    total = sum(raw.values())
    profile = {key: raw[key] / total for key in _PHASE_ORDER}

    return profile


def feasible_phases(
    engagement_time_s: float,
    threshold: float = 0.1,
) -> list[str]:
    """Return the phases whose budget share meets ``threshold``.

    The list preserves the canonical OODA order: ``observe``, ``orient``,
    ``decide``, ``act``.

    Parameters
    ----------
    engagement_time_s : float
        Available reaction time in seconds. Must be strictly positive.
    threshold : float, optional
        Minimum normalised budget share for a phase to be considered
        feasible. Defaults to ``0.1``.

    Returns
    -------
    list[str]
        Subset of ``("observe", "orient", "decide", "act")`` whose share in
        :func:`latency_profile` is ``>= threshold``, in canonical order.

    Raises
    ------
    ValueError
        If ``engagement_time_s`` is not strictly positive.
    """
    profile = latency_profile(engagement_time_s)
    return [phase for phase in _PHASE_ORDER if profile[phase] >= threshold]
