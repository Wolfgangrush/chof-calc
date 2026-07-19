"""Human oversight modality weighting by system transparency.

This module maps a system's transparency class to an oversight-modality
weight vector. The three modalities correspond to the temporal phases
of human oversight of an automated or AI system:

    * ``ex_ante_constraint``     -- constraints applied before deployment
                                    (e.g. design reviews, red-teaming,
                                    pre-deployment certification).
    * ``in_flight_supervision``  -- monitoring and oversight during
                                    operation (e.g. human-on-the-loop,
                                    runtime guards, kill-switches).
    * ``ex_post_audit``          -- review after deployment / after the
                                    fact (e.g. incident review, audit,
                                    accountability proceedings).

Rationale
---------
A black box cannot be constrained before deployment because its logic
cannot be inspected, so oversight weight must shift toward in-flight
supervision and ex-post audit. A white box exposes its internals and
therefore supports strong ex-ante constraints. A glass box sits between
the two and spreads weight roughly evenly across the three phases.
"""

from __future__ import annotations

from typing import Final

# Canonical weight vectors keyed by transparency class. Every vector
# sums to 1.0 and assigns a value in [0, 1] to each of the three
# modality keys.
_WEIGHTS: Final[dict[str, dict[str, float]]] = {
    "black_box": {
        "ex_ante_constraint": 0.10,
        "in_flight_supervision": 0.35,
        "ex_post_audit": 0.55,
    },
    "glass_box": {
        "ex_ante_constraint": 0.34,
        "in_flight_supervision": 0.33,
        "ex_post_audit": 0.33,
    },
    "white_box": {
        "ex_ante_constraint": 0.55,
        "in_flight_supervision": 0.30,
        "ex_post_audit": 0.15,
    },
}

# Canonical modality keys, in the order they appear in every weight vector.
_MODALITY_KEYS: Final[tuple[str, ...]] = (
    "ex_ante_constraint",
    "in_flight_supervision",
    "ex_post_audit",
)


def oversight_modality(transparency: str) -> dict[str, float]:
    """Return the oversight-modality weight vector for a transparency class.

    The returned mapping has exactly the keys
    ``"ex_ante_constraint"``, ``"in_flight_supervision"``, and
    ``"ex_post_audit"``. Every value lies in ``[0, 1]`` and the values
    sum to ``1.0``.

    A ``black_box`` cannot be constrained before deployment because its
    logic cannot be inspected, so oversight weight shifts to in-flight
    supervision and ex-post audit. A ``white_box`` exposes its internals
    and supports strong ex-ante constraints. A ``glass_box`` is the
    intermediate case where weight is roughly balanced across phases.

    Parameters
    ----------
    transparency:
        One of ``"black_box"``, ``"glass_box"``, ``"white_box"``.

    Returns
    -------
    dict[str, float]
        A fresh mapping from modality key to its weight.

    Raises
    ------
    ValueError
        If ``transparency`` is not a recognized transparency class.
    """
    if transparency not in _WEIGHTS:
        valid = ", ".join(repr(k) for k in _WEIGHTS)
        raise ValueError(
            f"unknown transparency {transparency!r}; expected one of: {valid}"
        )
    # Return a fresh dict so callers cannot mutate the module-level table.
    return dict(_WEIGHTS[transparency])


def dominant_modality(transparency: str) -> str:
    """Return the modality key with the highest weight for a transparency.

    Ties are broken in favor of the modality that appears first in the
    canonical order ``("ex_ante_constraint", "in_flight_supervision",
    "ex_post_audit")``, so the result is deterministic.

    Parameters
    ----------
    transparency:
        One of ``"black_box"``, ``"glass_box"``, ``"white_box"``.

    Returns
    -------
    str
        The modality key whose weight is largest for the given class.
        For ``"black_box"`` this is ``"ex_post_audit"``; for
        ``"glass_box"`` and ``"white_box"`` this is
        ``"ex_ante_constraint"``.

    Raises
    ------
    ValueError
        If ``transparency`` is not a recognized transparency class.
    """
    weights = oversight_modality(transparency)
    # ``max`` iterates dict keys in insertion order on ties; the canonical
    # insertion order is the order in _MODALITY_KEYS, which is exactly the
    # tie-break order we want.
    return max(_MODALITY_KEYS, key=weights.get)
