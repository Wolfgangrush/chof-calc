"""
Command-line interface for chof-calc.

Usage:
    chof-calc assess --system mq9
    chof-calc assess --system mq9 --json
    chof-calc list
    chof-calc explain
    chof-calc version
"""

from __future__ import annotations

import argparse
import json as json_module
import sys

from chof_calc import __version__
from chof_calc.equation import HEquation
from chof_calc.systems import get_fixture, list_fixtures


def _banner() -> str:
    return (
        "==============================================================\n"
        "  CHOF-CALC v" + __version__ + "\n"
        "  Quantifying Human Oversight for Autonomous Weapon Systems\n"
        "  Operationalising the H equation from Mahajan (2024)\n"
        "  QUB LLM Dissertation -- Apache 2.0 -- DOI: pending Zenodo\n"
        "=============================================================="
    )


def _render_severity(severity: str) -> str:
    return {
        "low": "[ LOW ]      autonomy permissible at this level",
        "medium": "[ MEDIUM ]   moderate human oversight needed",
        "high": "[ HIGH ]     high human oversight needed",
        "critical": "[ CRITICAL ] near-total human control required",
    }.get(severity, severity)


def cmd_list(args: argparse.Namespace) -> int:
    print(_banner())
    print()
    print("Baseline weapon-system fixtures:")
    print()
    print(f"  {'ID':<14}{'NAME':<22}{'YEAR':<8}{'TRANSPARENCY':<14}{'STATUS'}")
    print(f"  {'-' * 14}{'-' * 22}{'-' * 8}{'-' * 14}{'-' * 14}")
    for fx in list_fixtures():
        status = "provisional" if fx.provisional else "dissertation"
        print(
            f"  {fx.id:<14}{fx.name:<22}{fx.year_of_service:<8}"
            f"{fx.transparency.value:<14}{status}"
        )
    print()
    print(f"  Total: {len(list_fixtures())} fixtures.")
    return 0


def cmd_assess(args: argparse.Namespace) -> int:
    try:
        fixture = get_fixture(args.system)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    result = HEquation.compute(
        elements=fixture.elements,
        weights=fixture.weights,
        transparency=fixture.transparency,
        dissertation_published_value=fixture.dissertation_published_value,
    )

    if args.json:
        out = {
            "system": {
                "id": fixture.id,
                "name": fixture.name,
                "type": fixture.system_type,
                "manufacturer": fixture.manufacturer,
                "year_of_service": fixture.year_of_service,
                "transparency_class": fixture.transparency.value,
                "provisional": fixture.provisional,
            },
            "result": result.as_dict(),
        }
        print(json_module.dumps(out, indent=2))
        return 0

    # Human-readable assessment report.
    print(_banner())
    print()
    print("SYSTEM ASSESSED")
    print(f"  Name:          {fixture.name}")
    print(f"  Type:          {fixture.system_type}")
    print(f"  Manufacturer:  {fixture.manufacturer}")
    print(f"  Year:          {fixture.year_of_service}")
    print(f"  Transparency:  {fixture.transparency.value}")
    if fixture.provisional:
        print()
        print("  ! PROVISIONAL VALUES -- pending expert-panel scoring per")
        print("    Mahajan (2024) Ch 5.3. Do not use for operational decisions.")
    print()

    print("ELEMENT SCORES (score band [1, 45])")
    print(f"  {'Element':<32}{'Score':<8}{'Weight':<10}{'Contribution'}")
    print(f"  {'-' * 32}{'-' * 8}{'-' * 10}{'-' * 14}")
    elem_dict = fixture.elements.as_dict()
    wt_dict = fixture.weights.as_dict()
    from chof_calc.elements import ELEMENT_LABELS, Element

    for el in Element:
        score = elem_dict[el]
        wt = wt_dict[el]
        contrib = result.element_contributions[el]
        label = f"{el.value} -- {ELEMENT_LABELS[el]}"
        print(f"  {label:<32}{score:<8.2f}{wt:<10.4f}{contrib:.4f}")
    print(
        f"  {'TOTAL':<32}{'':<8}{result.weight_total:<10.4f}{result.weighted_sum:.4f}"
    )
    print()

    print("LIVE COMPUTATION (the equation walked through):")
    for line in result.computation_trace:
        print(f"  {line}")
    print()

    print("RESULT")
    print(f"  H_quantity:    {result.h_quantity:.4f} %")
    print(f"  Severity:      {_render_severity(result.severity.value)}")
    print()

    print("H_MODALITY (transparency-class aware oversight prescription)")
    print(f"  Class:                 {fixture.transparency.value}")
    print(f"  CHOF blocks available: {fixture.transparency.cohf_blocks}")
    print("  In-flight supervision: ", end="")
    print(
        "feasible"
        if fixture.transparency.supports_in_flight_supervision
        else "INFEASIBLE"
    )
    print("  Recommended modality:")
    # word-wrap the modality string at ~70 chars
    modality = fixture.transparency.recommended_modality
    words = modality.split()
    line = "    "
    for w in words:
        if len(line) + len(w) > 74:
            print(line)
            line = "    "
        line += w + " "
    if line.strip():
        print(line.rstrip())
    print()

    if result.correction_note:
        print("DOCUMENTED CORRECTION TO PUBLISHED DISSERTATION")
        words = result.correction_note.split()
        line = "  "
        for w in words:
            if len(line) + len(w) > 74:
                print(line)
                line = "  "
            line += w + " "
        if line.strip():
            print(line.rstrip())
        print()

    print("NOTES")
    words = fixture.notes.split()
    line = "  "
    for w in words:
        if len(line) + len(w) > 74:
            print(line)
            line = "  "
        line += w + " "
    if line.strip():
        print(line.rstrip())
    print()

    print(
        "CITATION: Mahajan, R. R. (2024). What Balance Between Human Oversight\n"
        "and Machine Autonomy Is Necessary To Uphold Ethical Standards in\n"
        "Warfare, and How Can This Balance Be Legally Codified and Enforced.\n"
        "LLM Dissertation, Queen's University Belfast, School of Law."
    )
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    print(_banner())
    print()
    print(
        "THE H EQUATION\n"
        "\n"
        "  Given a weapon system, the Human Oversight (H) score quantifies\n"
        "  what percentage of the engagement decision must remain under\n"
        "  human control (vs delegated to the autonomous system).\n"
        "\n"
        "             1     N\n"
        "    H = 100 - --- . Sigma (W_i . c_i)\n"
        "            SUM_W  i=1\n"
        "\n"
        "  where:\n"
        "    i in {RR, CC, EE, TT, SS, AA, II}   (the seven CHOF elements)\n"
        "    c_i in [1, 45]                      (element score)\n"
        "    W_i in [0, 1]                       (element weight; SUM_W = 1)\n"
        "\n"
        "THE SEVEN ELEMENTS\n"
        "\n"
        "  RR -- Risk Level\n"
        "  CC -- Operational Complexity\n"
        "  EE -- Ethical & Legal Compliance\n"
        "  TT -- Technological Reliability\n"
        "  SS -- Safety Concerns\n"
        "  AA -- Accuracy of Targeting\n"
        "  II -- Accountability Issues\n"
        "\n"
        "EVOLUTION: H_v1 -> H_v2\n"
        "\n"
        "  H_v1 (Mahajan 2024 dissertation) returns a single scalar H.\n"
        "  H_v2 (this tool) returns a vector:\n"
        "    - H_quantity        (the scalar score, kept as regression anchor)\n"
        "    - H_modality        (transparency-class aware: black/glass/white box)\n"
        "    - H_latency_profile (OODA-phase oversight distribution; future story)\n"
        "    - H_time_curve      (deployment-phase weight evolution; future story)\n"
        "    - H_counterfactual  (Pasquale-derived harm metric; future story)\n"
        "\n"
        "  v0.1.0-alpha ships H_quantity + H_modality. Other outputs land per\n"
        "  BMAD-PLAN.md Story sequence.\n"
        "\n"
        "FOR MORE: see https://github.com/wolfgang-rush/chof-calc"
    )
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    print(f"chof-calc {__version__}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="chof-calc",
        description=(
            "Quantifying Human Oversight for Autonomous Weapon Systems. "
            "Operationalises the H equation from Mahajan (2024) "
            "QUB LLM Dissertation."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_assess = subparsers.add_parser(
        "assess",
        help="Assess a weapon system and print its H score",
    )
    p_assess.add_argument(
        "--system",
        required=True,
        help="System id (e.g. mq9, iron_dome, sgr_a1, kargu_2, phalanx)",
    )
    p_assess.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of human-readable report",
    )
    p_assess.set_defaults(func=cmd_assess)

    p_list = subparsers.add_parser("list", help="List baseline fixtures")
    p_list.set_defaults(func=cmd_list)

    p_explain = subparsers.add_parser(
        "explain",
        help="Explain the H equation and the H_v1 -> H_v2 evolution",
    )
    p_explain.set_defaults(func=cmd_explain)

    p_version = subparsers.add_parser("version", help="Print version and exit")
    p_version.set_defaults(func=cmd_version)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
