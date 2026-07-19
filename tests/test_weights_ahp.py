import pytest
from chof_calc.weights_ahp import (
    ahp_weights as w,
    consistency_ratio as cr,
    is_consistent as ic,
)


def test_all_ones_equal_weights():
    ones = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    assert w(ones) == pytest.approx([1 / 3, 1 / 3, 1 / 3])
    assert cr(ones) == pytest.approx(0.0, abs=1e-9)


def test_weights_sum_to_one():
    A = [[1, 3, 5], [1 / 3, 1, 2], [1 / 5, 1 / 2, 1]]
    assert sum(w(A)) == pytest.approx(1.0)


def test_consistent_matrix_recovers_priority_and_cr_zero():
    p = [0.5, 0.3, 0.2]
    A = [[p[i] / p[j] for j in range(3)] for i in range(3)]
    assert w(A) == pytest.approx(p, abs=1e-6)
    assert cr(A) == pytest.approx(0.0, abs=1e-6)
    assert ic(A)


def test_inconsistent_matrix_flagged():
    B = [[1, 5, 9], [1 / 5, 1, 2], [1 / 9, 1 / 2, 1]]
    assert cr(B) > 0


@pytest.mark.parametrize(
    "bad", [[[1, 2], [3, 4], [5, 6]], [[1, -2], [-0.5, 1]], [[1, 0], [0, 1]]]
)
def test_invalid_raises(bad):
    with pytest.raises(ValueError):
        w(bad)
