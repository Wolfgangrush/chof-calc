"""Validation battery for the chof_calc human-oversight assessment framework.

This script exercises the public API of the (already installed) ``chof_calc``
package across the full Cartesian product of fixtures, engagement times,
deployment phases, exposure levels, and defense-in-depth layer counts. It
asserts a fixed set of mathematical invariants (INV1..INV8), accumulates every
failure without stopping on the first one, prints a per-invariant PASS/FAIL
tally plus the total number of combinations tested, and exits non-zero if any
invariant is violated.

Standard library only (json, itertools, math, sys), plus the ``chof_calc``
package under test.
"""

import itertools
import json
import math
import sys

from chof_calc.systems.fixtures import list_fixtures
from chof_calc.h_v2 import compute_h_v2
from chof_calc.export_jsonld import to_jsonld


TOL = 1e-9

ENGAGEMENT_TIMES = [0.001, 0.5, 1.0, 5.0, 15.0, 30.0, 60.0, 120.0]
DEPLOYMENT_PHASES = ["pre_deployment", "active", "post_deployment"]
EXPOSURES = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
N_LAYERS = [1, 2, 3, 4, 5]
LATENCY_KEYS = ("observe", "orient", "decide", "act")
INVARIANT_IDS = ("INV1", "INV2", "INV3", "INV4", "INV5", "INV6", "INV7", "INV8")


def approx_equal(a, b, tol=TOL):
    """Return True when ``a`` and ``b`` are equal within ``tol`` (default 1e-9)."""
    return abs(a - b) <= tol


def is_number(x):
    """True for real ints/floats, but not booleans."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def safe_fsum(values):
    """``math.fsum`` that yields NaN if any value is non-numeric."""
    try:
        return math.fsum(values)
    except TypeError:
        return float("nan")


def fixture_label(fixture):
    fid = getattr(fixture, "id", None)
    return str(fid) if fid is not None else repr(fixture)


def main():
    fixtures = list_fixtures()

    # Each failure is a (invariant_id, combo_description, message) tuple.
    failures = []
    tally = {inv: {"pass": 0, "fail": 0} for inv in INVARIANT_IDS}

    def record(invariant_id, combo, message):
        failures.append((invariant_id, combo, message))
        if invariant_id in tally:
            tally[invariant_id]["fail"] += 1

    total_combinations = 0

    # ------------------------------------------------------------------
    # INV1..INV6 across the full Cartesian product.
    # ------------------------------------------------------------------
    for fixture in fixtures:
        label = fixture_label(fixture)
        for (t, phase, exposure, n) in itertools.product(
                ENGAGEMENT_TIMES, DEPLOYMENT_PHASES, EXPOSURES, N_LAYERS):
            total_combinations += 1
            combo = ("fixture=%s engagement_time_s=%s deployment_phase=%s "
                     "exposure=%s n_layers=%s" % (label, t, phase, exposure, n))

            try:
                result = compute_h_v2(
                    fixture,
                    engagement_time_s=t,
                    deployment_phase=phase,
                    exposure=exposure,
                    n_layers=n,
                )
            except Exception as exc:  # defensive: never abort the sweep
                record("COMPUTE", combo,
                       "compute_h_v2 raised %s: %s" % (type(exc).__name__, exc))
                continue

            if not isinstance(result, dict):
                record("COMPUTE", combo,
                       "compute_h_v2 returned non-dict %s" % type(result).__name__)
                continue

            # INV1: 0.0 <= h_quantity <= 100.0
            hq = result.get("h_quantity")
            if is_number(hq) and 0.0 <= hq <= 100.0:
                tally["INV1"]["pass"] += 1
            else:
                record("INV1", combo, "h_quantity=%r outside [0, 100]" % (hq,))

            # INV2: h_modality has exactly 3 keys, sum(values) == 1.0 (1e-9)
            mod = result.get("h_modality")
            mod_ok = (
                isinstance(mod, dict)
                and len(mod) == 3
                and all(is_number(v) for v in mod.values())
                and approx_equal(math.fsum(mod.values()), 1.0)
            )
            if mod_ok:
                tally["INV2"]["pass"] += 1
            else:
                if isinstance(mod, dict):
                    detail = "keys=%r sum=%r" % (sorted(mod), safe_fsum(mod.values()))
                else:
                    detail = "type=%s" % type(mod).__name__
                record("INV2", combo, "h_modality invalid (%s)" % detail)

            # INV3: h_latency_profile has exactly the 4 OODA keys, sum == 1.0
            lat = result.get("h_latency_profile")
            lat_ok = (
                isinstance(lat, dict)
                and len(lat) == 4
                and set(lat.keys()) == set(LATENCY_KEYS)
                and all(is_number(v) for v in lat.values())
                and approx_equal(math.fsum(lat.values()), 1.0)
            )
            if lat_ok:
                tally["INV3"]["pass"] += 1
            else:
                if isinstance(lat, dict):
                    detail = "keys=%r sum=%r" % (sorted(lat), safe_fsum(lat.values()))
                else:
                    detail = "type=%s" % type(lat).__name__
                record("INV3", combo, "h_latency_profile invalid (%s)" % detail)

            # INV4: h_counterfactual_cost >= 0.0
            cc = result.get("h_counterfactual_cost")
            if is_number(cc) and cc >= 0.0:
                tally["INV4"]["pass"] += 1
            else:
                record("INV4", combo, "h_counterfactual_cost=%r is negative" % (cc,))

            # INV5: len(defense_in_depth) == n_layers, every coverage in [0, 1]
            did = result.get("defense_in_depth")
            if isinstance(did, list):
                did_len = len(did)
                cov_ok = all(
                    isinstance(layer, dict)
                    and "coverage" in layer
                    and is_number(layer["coverage"])
                    and 0.0 <= layer["coverage"] <= 1.0
                    for layer in did
                )
            else:
                did_len = None
                cov_ok = False
            if isinstance(did, list) and did_len == n and cov_ok:
                tally["INV5"]["pass"] += 1
            else:
                record("INV5", combo,
                       "defense_in_depth invalid (len=%r expected=%r)" % (did_len, n))

            # INV6: to_jsonld -> json.dumps -> json.loads round-trip
            rt_error = None
            rt = None
            try:
                ld = to_jsonld(result)
                rt = json.loads(json.dumps(ld))
            except Exception as exc:  # defensive
                rt_error = "%s: %s" % (type(exc).__name__, exc)

            if rt_error is not None:
                record("INV6", combo, "round-trip raised %s" % rt_error)
            else:
                msgs = []
                if "@type" not in rt:
                    msgs.append("missing '@type'")
                for k, v in result.items():
                    if k not in rt:
                        msgs.append("missing key %r" % (k,))
                        break
                    if rt[k] != v:
                        msgs.append("value mismatch for %r (rt=%r != orig=%r)"
                                    % (k, rt[k], v))
                        break
                if not msgs:
                    orig_hq = result.get("h_quantity")
                    rt_hq = rt.get("h_quantity")
                    if rt_hq != orig_hq:
                        msgs.append("h_quantity changed (rt=%r != orig=%r)"
                                    % (rt_hq, orig_hq))
                if msgs:
                    record("INV6", combo, "; ".join(msgs))
                else:
                    tally["INV6"]["pass"] += 1

    # ------------------------------------------------------------------
    # INV7: monotone exposure (controlled comparison).
    # ------------------------------------------------------------------
    for fixture in fixtures:
        label = fixture_label(fixture)
        points = []
        sweep_failed = False
        for exposure in EXPOSURES:
            combo = ("fixture=%s INV7 monotone-exposure "
                     "(engagement_time_s=30.0 deployment_phase=active n_layers=3 "
                     "exposure=%s)" % (label, exposure))
            try:
                r = compute_h_v2(fixture, engagement_time_s=30.0,
                                 deployment_phase="active",
                                 exposure=exposure, n_layers=3)
                points.append((exposure, r["h_counterfactual_cost"]))
            except Exception as exc:
                record("INV7", combo,
                       "compute_h_v2 raised %s: %s" % (type(exc).__name__, exc))
                sweep_failed = True
        if sweep_failed:
            continue
        monotone = True
        for (e0, c0), (e1, c1) in zip(points, points[1:]):
            if c1 < c0 - TOL:
                record("INV7",
                       "fixture=%s INV7 monotone-exposure sweep" % label,
                       "h_counterfactual_cost decreased: exposure %s->%s "
                       "cost %r->%r" % (e0, e1, c0, c1))
                monotone = False
        if monotone:
            tally["INV7"]["pass"] += 1

    # ------------------------------------------------------------------
    # INV8: time curve (controlled comparison).
    # ------------------------------------------------------------------
    for fixture in fixtures:
        label = fixture_label(fixture)
        combo = "fixture=%s INV8 time-curve" % label
        try:
            active = compute_h_v2(fixture, deployment_phase="active")["h_time_curve"]
            post = compute_h_v2(fixture, deployment_phase="post_deployment")["h_time_curve"]
            pre = compute_h_v2(fixture, deployment_phase="pre_deployment")["h_time_curve"]
        except Exception as exc:
            record("INV8", combo,
                   "compute_h_v2 raised %s: %s" % (type(exc).__name__, exc))
            continue
        if (active + TOL >= post) and (active + TOL >= pre):
            tally["INV8"]["pass"] += 1
        else:
            record("INV8", combo,
                   "active h_time_curve=%r not >= both post=%r and pre=%r"
                   % (active, post, pre))

    # ------------------------------------------------------------------
    # Report.
    # ------------------------------------------------------------------
    print("Total combinations tested: %d" % total_combinations)
    print()
    print("Per-invariant tally:")
    for inv in INVARIANT_IDS:
        p = tally[inv]["pass"]
        f = tally[inv]["fail"]
        status = "PASS" if f == 0 else "FAIL"
        print("  %s: %s (%d/%d checks)" % (inv, status, p, p + f))

    if failures:
        print()
        print("Failures (%d):" % len(failures))
        for inv, combo, msg in failures:
            print("  [%s] %s :: %s" % (inv, combo, msg))
        return 1

    print("ALL INVARIANTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
