"""Weapon systems transparency classification.

A weapon system's transparency class summarizes how observable and
predictable its internal behavior is, based on three normalized
attributes in [0, 1]:

* **Black box** — opaque: behavior cannot be inspected and is not
  deterministic or documented from the outside.
* **Glass box** — partially translucent: some combination of inspection,
  determinism, and documentation is available, but full insight into
  internal state and decision-making is missing.
* **White box** — fully transparent: the system can be inspected
  directly, behaves deterministically given the same inputs, and is
  thoroughly documented.

The transparency score is the arithmetic mean of the three
[0, 1] attributes. Boundaries used by :func:`classify_transparency` are
chosen so that ``(1, 1, 1)`` yields ``"white_box"``, ``(0, 0, 0)`` yields
``"black_box"``, and ``(0.5, 0.5, 0.5)`` yields ``"glass_box"``.
"""

from __future__ import annotations


def transparency_score(
    inspectability: float,
    determinism: float,
    documentation: float,
) -> float:
    """Compute the transparency score from three [0, 1] attributes.

    The score is the arithmetic mean of ``inspectability``,
    ``determinism``, and ``documentation``.

    Args:
        inspectability: How readily the system's internal state and
            logic can be inspected. Must lie in ``[0, 1]``.
        determinism: How predictable the system's outputs are given
            the same inputs. Must lie in ``[0, 1]``.
        documentation: How thoroughly the system's design and behavior
            is documented externally. Must lie in ``[0, 1]``.

    Returns:
        The arithmetic mean of the three attributes, a float in
        ``[0, 1]``.

    Raises:
        ValueError: If any of the three arguments lies outside
            ``[0, 1]``.
    """
    if not (0.0 <= inspectability <= 1.0):
        raise ValueError(f"inspectability must be in [0, 1], got {inspectability!r}")
    if not (0.0 <= determinism <= 1.0):
        raise ValueError(f"determinism must be in [0, 1], got {determinism!r}")
    if not (0.0 <= documentation <= 1.0):
        raise ValueError(f"documentation must be in [0, 1], got {documentation!r}")
    return (inspectability + determinism + documentation) / 3.0


def classify_transparency(
    inspectability: float,
    determinism: float,
    documentation: float,
) -> str:
    """Classify a weapon system's transparency class.

    Combines :func:`transparency_score` with fixed thresholds to map a
    triple of ``[0, 1]`` attributes to one of three discrete classes:

    * ``"white_box"`` for score ``>= 0.67`` — fully transparent.
    * ``"glass_box"`` for ``0.34 <= score < 0.67`` — partially
      translucent.
    * ``"black_box"`` for score ``< 0.34`` — opaque.

    Args:
        inspectability: Inspectability attribute in ``[0, 1]``.
        determinism: Determinism attribute in ``[0, 1]``.
        documentation: Documentation attribute in ``[0, 1]``.

    Returns:
        One of ``"white_box"``, ``"glass_box"``, or ``"black_box"``.

    Raises:
        ValueError: If any of the three arguments lies outside
            ``[0, 1]`` (raised by :func:`transparency_score`).
    """
    score = transparency_score(inspectability, determinism, documentation)
    if score >= 0.67:
        return "white_box"
    if score >= 0.34:
        return "glass_box"
    return "black_box"
