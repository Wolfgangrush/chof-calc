"""Serialise a CHOF H_v2 assessment to JSON-LD."""

from __future__ import annotations

import json
from typing import Any


def to_jsonld(
    h_v2_result: dict[str, Any],
    *,
    base: str = "https://chof.example/vocab#",
) -> dict[str, Any]:
    """Serialise a CHOF H_v2 assessment dict into a JSON-LD document.

    The returned document contains an ``@context`` object that maps every term
    in ``h_v2_result`` to ``base + term``, an ``@type`` of
    ``"OversightAssessment"``, and the original values embedded under their
    term keys. The numeric ``h_quantity`` value is preserved exactly.
    """
    document: dict[str, Any] = {
        "@context": {term: base + term for term in h_v2_result},
        "@type": "OversightAssessment",
    }
    for term, value in h_v2_result.items():
        document[term] = value
    return document


def to_jsonld_str(
    h_v2_result: dict[str, Any],
    *,
    base: str = "https://chof.example/vocab#",
) -> str:
    """Return :func:`to_jsonld` serialised as a pretty-printed JSON string."""
    return json.dumps(to_jsonld(h_v2_result, base=base), indent=2, sort_keys=True)
