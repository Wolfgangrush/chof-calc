"""
Baseline weapon-system fixtures for the H equation.

Each fixture provides:
  - elements (the 7 element scores)
  - weights (the 7 weights)
  - transparency class
  - metadata (name, type, manufacturer, year)
  - dissertation_published_value (where available — for regression testing)
"""

from chof_calc.systems.fixtures import (
    SystemFixture,
    IRON_DOME,
    KARGU_2,
    MQ9_REAPER,
    PHALANX,
    SGR_A1,
    REGISTRY,
    get_fixture,
    list_fixtures,
)

__all__ = [
    "SystemFixture",
    "IRON_DOME",
    "KARGU_2",
    "MQ9_REAPER",
    "PHALANX",
    "SGR_A1",
    "REGISTRY",
    "get_fixture",
    "list_fixtures",
]
