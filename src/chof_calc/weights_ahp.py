from __future__ import annotations

import math

#: Random-index (RI) table for matrix sizes 1..10 (Saaty, 1980).
RI: dict[int, float] = {
    1: 0.0,
    2: 0.0,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
}


def _validate_matrix(matrix: list[list[float]]) -> int:
    """Validate that ``matrix`` is a square n x n list of positive numbers.

    Returns the dimension ``n``. Raises :class:`ValueError` for any structural
    or positivity problem.
    """
    if not isinstance(matrix, list) or len(matrix) == 0:
        raise ValueError("matrix must be a non-empty list of rows")
    n = len(matrix)
    for i, row in enumerate(matrix):
        if not isinstance(row, list):
            raise ValueError(f"row {i} is not a list")
        if len(row) != n:
            raise ValueError(
                f"matrix is not square: row {i} has length {len(row)}, expected {n}"
            )
        for j, entry in enumerate(row):
            if isinstance(entry, bool) or not isinstance(entry, (int, float)):
                raise ValueError(f"entry at ({i},{j}) is not a real number")
            if not (math.isfinite(entry) and entry > 0.0):
                raise ValueError(f"entry at ({i},{j}) must be a positive finite number")
    return n


def ahp_weights(matrix: list[list[float]]) -> list[float]:
    """Compute Saaty AHP priority weights via the geometric-mean method.

    For each row ``i``, the geometric mean
    ``g_i = (prod_j matrix[i][j]) ** (1 / n)`` is taken and the resulting
    vector is normalized so the weights sum to ``1.0``.

    Parameters
    ----------
    matrix:
        An ``n x n`` positive reciprocal pairwise-comparison matrix.

    Returns
    -------
    list[float]
        Priority weights whose entries sum to ``1.0``.

    Raises
    ------
    ValueError
        If ``matrix`` is not square, has ``n < 1``, or contains any
        non-positive entry.
    """
    n = _validate_matrix(matrix)
    raw: list[float] = []
    for row in matrix:
        product = 1.0
        for entry in row:
            product *= entry
        raw.append(product ** (1.0 / n))
    total = math.fsum(raw)
    if total <= 0.0:
        # Defensive: with all-positive entries and the product-to-the-1/n
        # operation this should not happen, but guard against pathological
        # floating-point values.
        raise ValueError("computed geometric means are non-positive")
    return [g / total for g in raw]


def consistency_ratio(matrix: list[list[float]]) -> float:
    """Compute Saaty's consistency ratio (CR) for a pairwise-comparison matrix.

    ``w = ahp_weights(matrix)`` is the priority vector, ``Aw = matrix . w`` is
    the matrix-vector product, and ``lambda_max`` is the mean of ``Aw[i] / w[i]``.
    The consistency index is ``CI = (lambda_max - n) / (n - 1)`` and
    ``CR = CI / RI_n``. For ``n <= 2`` or when ``RI_n == 0`` the function
    returns ``0.0``.

    Parameters
    ----------
    matrix:
        An ``n x n`` positive reciprocal pairwise-comparison matrix.

    Returns
    -------
    float
        The consistency ratio. ``0.0`` indicates perfect consistency (or an
        ``n <= 2`` case for which CR is undefined but conventionally 0).

    Raises
    ------
    ValueError
        If ``matrix`` is not square, has ``n < 1``, or contains any
        non-positive entry.
    """
    n = _validate_matrix(matrix)
    if n <= 2:
        return 0.0
    w = ahp_weights(matrix)
    # matrix-vector product Aw
    aw: list[float] = [math.fsum(row[j] * w[j] for j in range(n)) for row in matrix]
    ratios = [aw[i] / w[i] for i in range(n)]
    lambda_max = math.fsum(ratios) / n
    ci = (lambda_max - n) / (n - 1)
    ri_n = RI.get(n, 0.0)
    if ri_n > 0.0:
        return ci / ri_n
    return 0.0


def is_consistent(matrix: list[list[float]], threshold: float = 0.10) -> bool:
    """Return whether ``matrix`` is sufficiently consistent.

    A matrix is considered consistent when
    ``consistency_ratio(matrix) < threshold``. The classical Saaty threshold
    is ``0.10``.

    Parameters
    ----------
    matrix:
        An ``n x n`` positive reciprocal pairwise-comparison matrix.
    threshold:
        Maximum acceptable consistency ratio (default ``0.10``).

    Returns
    -------
    bool
        ``True`` iff ``consistency_ratio(matrix) < threshold``.
    """
    return consistency_ratio(matrix) < threshold
