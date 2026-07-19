import pytest
from chof_calc.defense_in_depth import (
    plan_layers,
    combined_coverage,
    layer_independence_ok,
    FAILURE_MODES,
)


@pytest.mark.parametrize("h", [0, 50, 75, 99])
@pytest.mark.parametrize("n", [1, 2, 3])
def test_combined_coverage_reconstructs_h(h, n):
    layers = plan_layers(h, n)
    assert len(layers) == n
    assert combined_coverage(layers) == pytest.approx(h / 100.0)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_layers_independent_and_distinct(n):
    layers = plan_layers(60, n)
    assert layer_independence_ok(layers) is True
    assert len({x["failure_mode"] for x in layers}) == n


def test_failure_modes_come_from_registry():
    for layer in plan_layers(80, 3):
        assert layer["failure_mode"] in FAILURE_MODES


@pytest.mark.parametrize(
    "bad", [(150, 3), (-1, 3), (50, 0), (50, len(FAILURE_MODES) + 1)]
)
def test_invalid_raises(bad):
    with pytest.raises(ValueError):
        plan_layers(*bad)
