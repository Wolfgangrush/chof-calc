"""
Transparency-class classification — H_v2 enrichment (Story S11).

Each autonomous weapon system falls into one of three transparency classes
based on how inspectable its decision pipeline is. The class determines
which CHOF blocks (Verdiesen, Santoni de Sio & Dignum 2020 Fig 4.2) are
available for human oversight to attach to.

This is the H_v2 modality output — solves the dissertation's gap where
H_v1 prescribed the same oversight regardless of system architecture.
"""

from __future__ import annotations

from enum import Enum


class TransparencyClass(str, Enum):
    """Transparency class of an autonomous weapon system."""

    BLACK_BOX = "black_box"
    """Closed-weight neural network. Inputs and outputs only; intermediate
    reasoning is not inspectable. Examples: MQ-9 image classifier, LLM-based
    threat assessor. In-flight human supervision is structurally impossible;
    oversight must attach ex-ante (Block 1: pre-deployment supervision,
    Block 4: ex-ante control via target-category whitelisting) and ex-post
    (Block 6: accountability audit, Block 3: post-deployment review)."""

    GLASS_BOX = "glass_box"
    """Opaque internals with engineered interpretability layer. Examples:
    modern CNN with Grad-CAM saliency overlays, attention-visualised
    transformer. Operator can intervene in real time but with high cognitive
    load. Oversight attaches to Block 1, Block 4, Block 5 (ongoing control),
    and Block 6."""

    WHITE_BOX = "white_box"
    """Symbolic AI; rule-based engagement; every decision path inspectable.
    Examples: Aegis Phalanx pre-programmed engagement rules. Oversight is
    primarily Block 4 (ex-ante rule verification); execution can be trusted
    once rules are verified."""

    @property
    def cohf_blocks(self) -> list[int]:
        """The CHOF blocks (Verdiesen et al. 2020 Fig 4.2) where oversight
        can structurally attach for this transparency class."""
        return {
            TransparencyClass.BLACK_BOX: [1, 3, 4, 6],
            TransparencyClass.GLASS_BOX: [1, 3, 4, 5, 6],
            TransparencyClass.WHITE_BOX: [1, 4, 6],
        }[self]

    @property
    def supports_in_flight_supervision(self) -> bool:
        """Whether real-time, in-flight human supervision is structurally
        feasible for this transparency class."""
        return self == TransparencyClass.GLASS_BOX

    @property
    def recommended_modality(self) -> str:
        """Human-readable oversight prescription for this class."""
        return {
            TransparencyClass.BLACK_BOX: (
                "Ex-ante constraint engineering (pre-mission target-category "
                "whitelisting) + ex-post audit (Article 36 review). "
                "In-flight supervision is structurally infeasible; do not "
                "rely on it."
            ),
            TransparencyClass.GLASS_BOX: (
                "Continuous saliency-map supervision during deployment + "
                "pre-mission target-category whitelisting + post-mission "
                "Article 36 audit. Real-time intervention is possible but "
                "imposes high operator cognitive load."
            ),
            TransparencyClass.WHITE_BOX: (
                "Ex-ante rule verification (review engagement rules before "
                "mission) + ex-post audit. Once rules are verified, execution "
                "can be trusted within rule envelope."
            ),
        }[self]
