"""Layered (Swiss-cheese) oversight-architecture planner.

This module provides utilities for designing a defense-in-depth oversight
architecture. Each layer covers an independent failure mode; the combined
probability of catching an issue is computed under an independence
assumption (the "Swiss-cheese" model).
"""

from __future__ import annotations

import math
from typing import List, Dict


#: The independent failure modes each layer is responsible for covering.
FAILURE_MODES: List[str] = [
    "sensor_failure",
    "classifier_error",
    "operator_unavailable",
    "comms_loss",
    "geofence_breach",
]


def plan_layers(h_required: float, n_layers: int = 3) -> List[Dict]:
    """Plan ``n_layers`` oversight layers achieving combined coverage ``h_required``.

    The per-layer coverage ``c`` is computed so that, assuming independence,
    ``n_layers`` layers of coverage ``c`` combine to ``h_required/100``::

        h_required/100 = 1 - (1 - c) ** n_layers
        c = 1 - (1 - h_required/100) ** (1 / n_layers)

    Parameters
    ----------
    h_required : float
        Required combined oversight percentage in the closed interval
        ``[0, 100]``. Values outside this range raise :class:`ValueError`.
    n_layers : int, optional
        Number of layers to produce. Must be an :class:`int` in
        ``[1, len(FAILURE_MODES)]``. Non-integer or out-of-range values
        raise :class:`ValueError`.

    Returns
    -------
    list[dict]
        Exactly ``n_layers`` dictionaries of the form
        ``{"index": i, "failure_mode": FAILURE_MODES[i], "coverage": c}``
        where ``i`` is the 0-based layer index and ``c`` is the per-layer
        coverage in ``[0, 1]``.
    """
    if not isinstance(h_required, (int, float)):
        raise ValueError(
            f"h_required must be a number in [0, 100], got {type(h_required).__name__}"
        )
    if isinstance(h_required, bool) or not (
        isinstance(h_required, (int, float))
        and 0.0 <= float(h_required) <= 100.0
    ):
        raise ValueError(
            f"h_required must be in [0, 100], got {h_required!r}"
        )

    if isinstance(n_layers, bool) or not isinstance(n_layers, int):
        raise ValueError(
            f"n_layers must be an int in [1, {len(FAILURE_MODES)}], "
            f"got {type(n_layers).__name__}"
        )
    if not 1 <= n_layers <= len(FAILURE_MODES):
        raise ValueError(
            f"n_layers must be in [1, {len(FAILURE_MODES)}], got {n_layers!r}"
        )

    n = int(n_layers)
    h = float(h_required) / 100.0

    if h <= 0.0:
        c = 0.0
    elif h >= 1.0:
        c = 1.0
    else:
        c = 1.0 - math.pow(1.0 - h, 1.0 / n)

    return [
        {
            "index": i,
            "failure_mode": FAILURE_MODES[i],
            "coverage": c,
        }
        for i in range(n)
    ]


def combined_coverage(layers: List[Dict]) -> float:
    """Compute combined coverage assuming layer independence.

    The combined coverage is ``1 - prod(1 - c_i)`` over all layers.

    Parameters
    ----------
    layers : list[dict]
        Layers as produced by :func:`plan_layers`. Each dict must contain
        a numeric ``"coverage"`` key in ``[0, 1]``.

    Returns
    -------
    float
        The combined coverage in ``[0, 1]``.
    """
    miss = 1.0
    for layer in layers:
        miss *= 1.0 - float(layer["coverage"])
    return 1.0 - miss


def layer_independence_ok(layers: List[Dict]) -> bool:
    """Return ``True`` iff every layer covers a distinct failure mode.

    Parameters
    ----------
    layers : list[dict]
        Layers as produced by :func:`plan_layers`. Each dict must contain
        a ``"failure_mode"`` key.

    Returns
    -------
    bool
        ``True`` if all ``failure_mode`` values are pairwise distinct.
    """
    seen = set()
    for layer in layers:
        mode = layer["failure_mode"]
        if mode in seen:
            return False
        seen.add(mode)
    return True
