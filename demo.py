"""Demo script for the CHOF H_v2 assessment tool.

This script illustrates how to use the CHOF (Counterfactual Harm Operational
Framework) H_v2 assessment on the bundled system fixtures. The results are
decision-support only: H_v2 makes the cost of less-safe options visible, it
does not by itself make autonomous weapon systems safe.
"""
from __future__ import annotations

import argparse
import sys
from typing import Any, Sequence

from chof_calc.systems.fixtures import list_fixtures
from chof_calc.h_v2 import compute_h_v2
from chof_calc.export_jsonld import to_jsonld_str


MQ9_ANCHOR_NOTE = (
    "Anchor note: for the MQ-9 fixture, h_quantity reproduces the dissertation "
    "value used as the validation anchor for H_v2."
)


def _format_h_quantity(value: float) -> str:
    """Render an h_quantity as a percentage string."""
    return f"{value:.2f}%"


def _format_counterfactual_cost(value: float) -> str:
    """Render an h_counterfactual_cost as counterfactual-casualties-equivalent."""
    return f"{value:.3f} counterfactual-casualties-equivalent"


def _print_fixture_block(result: dict[str, Any]) -> None:
    """Print a readable block summarizing a single fixture assessment."""
    print("-" * 72)
    print(f"System:                {result['system']}")
    print(f"h_quantity:            {_format_h_quantity(result['h_quantity'])}")
    print(f"severity:              {result['severity']}")
    print(f"transparency_class:    {result['transparency_class']}")
    print(f"dominant_modality:     {result['dominant_modality']}")
    print(f"h_time_curve:          {result['h_time_curve']}")
    print(
        "h_counterfactual_cost: "
        f"{_format_counterfactual_cost(result['h_counterfactual_cost'])}"
    )
    print(
        "defense_in_depth:      "
        f"{len(result['defense_in_depth'])} layer(s)"
    )
    print("-" * 72)


def _print_header() -> None:
    """Print the decision-support / advisory header."""
    print("CHOF H_v2 Assessment Tool — DECISION-SUPPORT ONLY")
    print("=" * 72)
    print(
        "This tool is advisory. It makes the cost of less-safe options visible; "
        "it does not, by itself, make autonomous weapon systems safe."
    )
    print()


def _run_default() -> None:
    """Run the default human-readable demo over every fixture."""
    _print_header()
    print(MQ9_ANCHOR_NOTE)
    print()
    for fixture in list_fixtures():
        result = compute_h_v2(fixture)
        _print_fixture_block(result)


def _run_jsonld() -> None:
    """Print JSON-LD for the first fixture's assessment."""
    fixtures = list_fixtures()
    first_fixture = fixtures[0]
    result = compute_h_v2(first_fixture)
    print(to_jsonld_str(result))


def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser for the demo CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Demonstrate the CHOF H_v2 assessment tool across system fixtures."
        )
    )
    parser.add_argument(
        "--jsonld",
        action="store_true",
        help=(
            "Print JSON-LD for the first fixture's H_v2 assessment instead of "
            "the human-readable default output."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the CHOF H_v2 demo script.

    Parameters
    ----------
    argv : Sequence[str] | None
        Optional argument list. When ``None``, ``sys.argv[1:]`` is used.

    Returns
    -------
    int
        ``0`` on success, ``1`` if an error is raised during execution.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.jsonld:
            _run_jsonld()
        else:
            _run_default()
    except Exception as exc:  # noqa: BLE001 — top-level demo guard
        print(f"Error: CHOF H_v2 demo failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
