from __future__ import annotations

"""Pasquale-style counterfactual-harm metric for sub-100% human oversight.

The module quantifies the *counterfactual* harm that arises when human
oversight of an automated system falls short of full coverage.  For a given
oversight percentage ``h_quantity`` (the fraction of decisions a human
actually reviews), the unmitigated-risk fraction is the gap

    gap = (100 - h_quantity) / 100

which is then scaled by an *exposure* factor describing the situational
harm potential of the deployment (e.g. civilian density) and by an upper
bound on the casualties that a fully unmitigated failure could cause.  The
result is a number expressed as *counterfactual-casualties-equivalent*:
the harm that *would* materialise if every un-reviewed decision went on to
realise its worst-case outcome.

This is a deliberately conservative (worst-case) estimator intended to
make the cost of any gap in human oversight legible at a glance.
"""

__all__ = ["counterfactual_cost", "marginal_cost_per_point"]


def _validate_exposure(exposure: float) -> None:
    """Reject ``exposure`` values outside the closed unit interval."""
    if not (0.0 <= exposure <= 1.0):
        raise ValueError(f"exposure must be in [0, 1]; got {exposure!r}")


def _validate_max_casualties(max_casualties: float) -> None:
    """Reject negative ``max_casualties`` upper bounds."""
    if max_casualties < 0.0:
        raise ValueError(f"max_casualties must be >= 0; got {max_casualties!r}")


def _validate_h_quantity(h_quantity: float) -> None:
    """Reject oversight percentages outside the closed 0..100 range."""
    if not (0.0 <= h_quantity <= 100.0):
        raise ValueError(f"h_quantity must be in [0, 100]; got {h_quantity!r}")


def counterfactual_cost(
    h_quantity: float,
    exposure: float,
    max_casualties: float = 100.0,
) -> float:
    """Return counterfactual-casualties-equivalent for a given oversight gap.

    Parameters
    ----------
    h_quantity:
        Human oversight percentage in the closed interval ``[0, 100]``.
        ``100`` means every decision is reviewed; ``0`` means no oversight
        at all.
    exposure:
        Situational harm potential in the closed unit interval ``[0, 1]``.
        Typical values include civilian density near an autonomous-system
        deployment zone.  ``0`` means the situation can never produce harm
        regardless of oversight; ``1`` means full worst-case exposure.
    max_casualties:
        Upper bound on casualties that a fully unmitigated failure could
        cause.  Must be non-negative.  Defaults to ``100.0``.

    Returns
    -------
    float
        The counterfactual-casualties-equivalent, equal to

        .. code-block:: text

            ((100 - h_quantity) / 100) * exposure * max_casualties

        The result is always non-negative and equals ``0`` exactly when
        ``h_quantity == 100`` (full oversight).

    Raises
    ------
    ValueError
        If ``h_quantity`` is outside ``[0, 100]``, ``exposure`` is outside
        ``[0, 1]``, or ``max_casualties`` is negative.
    """
    _validate_h_quantity(h_quantity)
    _validate_exposure(exposure)
    _validate_max_casualties(max_casualties)

    gap = (100.0 - h_quantity) / 100.0
    return gap * exposure * max_casualties


def marginal_cost_per_point(
    exposure: float,
    max_casualties: float = 100.0,
) -> float:
    """Return counterfactual harm added per one-point drop in ``h_quantity``.

    The marginal cost is the derivative of :func:`counterfactual_cost` with
    respect to ``h_quantity`` (in points): dropping oversight by one point
    adds ``exposure * max_casualties / 100`` casualties-equivalent.

    Parameters
    ----------
    exposure:
        Situational harm potential in the closed unit interval ``[0, 1]``.
    max_casualties:
        Upper bound on casualties for a fully unmitigated failure.  Must be
        non-negative.  Defaults to ``100.0``.

    Returns
    -------
    float
        The harm in counterfactual-casualties-equivalent units added per
        one-point decrease in ``h_quantity``.  Always non-negative.

    Raises
    ------
    ValueError
        If ``exposure`` is outside ``[0, 1]`` or ``max_casualties`` is
        negative.
    """
    _validate_exposure(exposure)
    _validate_max_casualties(max_casualties)

    return (exposure * max_casualties) / 100.0
