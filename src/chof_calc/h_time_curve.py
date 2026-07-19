from __future__ import annotations

"""Human-oversight emphasis across the weapon-system deployment lifecycle.

Models how human-oversight emphasis varies across a weapon system deployment
lifecycle. Active operation demands the fullest real-time oversight;
pre-deployment oversight is design-time constraint-setting; post-deployment
is audit-tier.
"""


_PHASE_MULTIPLIERS: dict[str, float] = {
    "pre_deployment": 0.70,
    "active": 1.00,
    "post_deployment": 0.40,
}


def phase_oversight_multiplier(deployment_phase: str) -> float:
    """Return the oversight multiplier for a given deployment phase.

    Active operation demands the fullest real-time oversight;
    pre-deployment oversight is design-time constraint-setting;
    post-deployment is audit-tier.
    """
    if deployment_phase not in _PHASE_MULTIPLIERS:
        raise ValueError(
            f"Unknown deployment phase: {deployment_phase!r}. "
            f"Expected one of: {sorted(_PHASE_MULTIPLIERS)}."
        )
    return _PHASE_MULTIPLIERS[deployment_phase]


def lifecycle_profile() -> dict[str, float]:
    """Return a mapping of every deployment phase to its oversight multiplier."""
    return dict(_PHASE_MULTIPLIERS)


def weighted_oversight(base_oversight: float, deployment_phase: str) -> float:
    """Return ``base_oversight`` scaled by the phase multiplier, clamped to [0, 1].

    ``base_oversight`` must lie in the closed interval [0, 1]; any other value
    raises ``ValueError``. The result is clamped to [0, 1] so that an active
    phase with maximum base oversight yields exactly 1.0 and never overflows.
    """
    if not 0.0 <= base_oversight <= 1.0:
        raise ValueError(f"base_oversight must be in [0, 1], got {base_oversight!r}.")
    weighted = base_oversight * phase_oversight_multiplier(deployment_phase)
    if weighted < 0.0:
        return 0.0
    if weighted > 1.0:
        return 1.0
    return weighted
