"""H_v2 vector aggregator for the CHOF (Cumulative Human Oversight Factor) framework.

This module composes the individual CHOF equation-core submodules into a single
H_v2 vector, providing a holistic view of human oversight for a given system
under a particular deployment context. It wraps:

- :class:`HEquation` — the core oversight quantity computation
- :class:`TransparencyClass` — the transparency regime of the system
- :mod:`chof_calc.h_modality` — oversight modality decomposition
- :mod:`chof_calc.ooda_phase_mapper` — OODA-loop latency profile
- :mod:`chof_calc.h_time_curve` — phase-based oversight multiplier
- :mod:`chof_calc.h_counterfactual` — counterfactual cost estimate
- :mod:`chof_calc.defense_in_depth` — layered defense plan

The two public entry points are :func:`compute_h_v2` (operate on a fixture
directly) and :func:`h_v2_for` (look up a fixture by system id).
"""
from __future__ import annotations

from chof_calc.equation import HEquation
from chof_calc.transparency import TransparencyClass
from chof_calc.h_modality import oversight_modality, dominant_modality
from chof_calc.ooda_phase_mapper import latency_profile
from chof_calc.h_time_curve import phase_oversight_multiplier
from chof_calc.h_counterfactual import counterfactual_cost
from chof_calc.defense_in_depth import plan_layers
from chof_calc.systems.fixtures import get_fixture


def compute_h_v2(
    fixture,
    *,
    engagement_time_s: float = 30.0,
    deployment_phase: str = "active",
    exposure: float = 0.5,
    n_layers: int = 3,
) -> dict:
    """Compute the full H_v2 oversight vector for ``fixture``.

    The function runs :meth:`HEquation.compute` against the fixture's
    elements, weights, and transparency regime, then enriches the result with
    modality decomposition, latency profiling, time-curve scaling,
    counterfactual cost, and a layered defense plan.

    :param fixture: A fixture object with ``id``, ``elements``, ``weights``,
        and ``transparency`` attributes. ``transparency`` may be a
        :class:`TransparencyClass` or any value whose string form is one of
        ``"black_box"``/``"glass_box"``/``"white_box"``.
    :param engagement_time_s: Engagement time in seconds, forwarded to
        :func:`latency_profile`.
    :param deployment_phase: Deployment phase label, forwarded to
        :func:`phase_oversight_multiplier`.
    :param exposure: Exposure scalar in ``[0, 1]``, forwarded to
        :func:`counterfactual_cost`.
    :param n_layers: Number of defense layers requested from
        :func:`plan_layers`.
    :returns: A dict containing every component of the H_v2 vector under
        stable keys (see module docstring).
    """
    res = HEquation.compute(fixture.elements, fixture.weights, fixture.transparency)
    h_q = res.h_quantity
    if isinstance(fixture.transparency, TransparencyClass):
        t_str = fixture.transparency.value
    else:
        t_str = str(fixture.transparency)

    return {
        "system": getattr(fixture, "id", None),
        "h_quantity": h_q,
        "severity": res.severity.value,
        "transparency_class": t_str,
        "h_modality": oversight_modality(t_str),
        "dominant_modality": dominant_modality(t_str),
        "h_latency_profile": latency_profile(engagement_time_s),
        "h_time_curve": phase_oversight_multiplier(deployment_phase),
        "h_counterfactual_cost": counterfactual_cost(h_q, exposure),
        "defense_in_depth": plan_layers(h_q, n_layers),
    }


def h_v2_for(system_id: str, **kwargs) -> dict:
    """Compute the H_v2 vector for the fixture identified by ``system_id``.

    Any additional keyword arguments are forwarded to :func:`compute_h_v2`.

    :param system_id: The fixture identifier passed to :func:`get_fixture`.
    :param kwargs: Forwarded to :func:`compute_h_v2`.
    :returns: The H_v2 vector dict produced by :func:`compute_h_v2`.
    """
    return compute_h_v2(get_fixture(system_id), **kwargs)
