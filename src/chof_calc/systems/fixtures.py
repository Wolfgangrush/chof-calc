"""
The five baseline weapon-system fixtures.

ONLY the MQ-9 Reaper fixture has values directly published in the
dissertation (Mahajan 2024 Ch 4.6 Simulation). The other four fixtures
(Iron Dome · SGR-A1 · Kargu-2 · Phalanx) carry PROVISIONAL values
synthesised from open-source descriptions in the dissertation's literature
review and must be re-scored by a multidisciplinary expert panel per
Mahajan 2024 Ch 5.3 before any operational use.

PROVISIONAL fixtures are tagged in their metadata. The CLI displays a
warning when a provisional fixture is assessed.
"""

from __future__ import annotations

from dataclasses import dataclass

from chof_calc.elements import Elements
from chof_calc.transparency import TransparencyClass
from chof_calc.weights import Weights


@dataclass(frozen=True)
class SystemFixture:
    """A baseline weapon-system fixture."""

    id: str
    name: str
    system_type: str
    manufacturer: str
    year_of_service: int
    elements: Elements
    weights: Weights
    transparency: TransparencyClass
    provisional: bool
    notes: str
    dissertation_published_value: float | None = None


# ============================================================================
# MQ-9 REAPER  --  dissertation-faithful (Mahajan 2024 Ch 4.6 + p.41-42)
# ============================================================================
#
# Values transcribed verbatim from Mahajan (2024) pp.41-42:
#   Risk Level (RR):              35
#   Operational Complexity (CC):  30
#   Ethical & Legal Compliance:   28
#   Technological Reliability:    20
#   Safety Concerns (SS):         25
#   Accuracy of Targeting (AA):   30
#   Accountability Issues (II):   32
#
# Weights:
#   W_RR = 0.25, W_CC = 0.15, W_EE = 0.15, W_TT = 0.10,
#   W_SS = 0.10, W_AA = 0.15, W_II = 0.10
#   SUM_W = 1.00
#
# Computation:
#   weighted_sum =  0.25*35 + 0.15*30 + 0.15*28 + 0.10*20
#                +  0.10*25 + 0.15*30 + 0.10*32
#                =  8.75 + 4.50 + 4.20 + 2.00 + 2.50 + 4.50 + 3.20
#                = 29.65
#   H            = 100 - 29.65 / 1.00 = 70.35 %
#
# The dissertation reports H = 75.35 % on p.42. The underlying weighted-sum
# (29.65) is computed correctly in the dissertation, but the final
# subtraction step contains an apparent arithmetic error
# (100 - 29.65 = 70.35, not 75.35). The tool reports the mathematically
# correct value 70.35 % and flags the discrepancy via the correction_note
# field of HResult. See README section "Documented Corrections to the
# Published Dissertation" for the full provenance discussion.
# ============================================================================
MQ9_REAPER = SystemFixture(
    id="mq9",
    name="MQ-9 Reaper",
    system_type="Unmanned Combat Aerial Vehicle (UCAV)",
    manufacturer="General Atomics Aeronautical Systems",
    year_of_service=2007,
    elements=Elements(RR=35, CC=30, EE=28, TT=20, SS=25, AA=30, II=32),
    weights=Weights(
        W_RR=0.25, W_CC=0.15, W_EE=0.15, W_TT=0.10,
        W_SS=0.10, W_AA=0.15, W_II=0.10,
    ),
    transparency=TransparencyClass.GLASS_BOX,
    provisional=False,
    notes=(
        "Dissertation-faithful regression anchor. Values published in "
        "Mahajan (2024) Ch 4.6 Simulation at pp.40-42. Hellfire-armed "
        "ISR/strike platform with human-in-the-loop engagement decision. "
        "Classed as glass box because targeting confidence and sensor data "
        "are surfaced to operator in real time, though underlying "
        "classifier is opaque."
    ),
    dissertation_published_value=75.35,
)


# ============================================================================
# IRON DOME -- PROVISIONAL; pending expert-panel scoring
# ============================================================================
# Israeli short-range rocket defence. Autonomous threat-detection +
# intercept-decision. Operates in seconds — no human-in-the-loop possible
# during engagement, by design.
IRON_DOME = SystemFixture(
    id="iron_dome",
    name="Iron Dome",
    system_type="Automated Short-Range Air Defence System",
    manufacturer="Rafael Advanced Defense Systems",
    year_of_service=2011,
    elements=Elements(RR=20, CC=25, EE=15, TT=15, SS=20, AA=20, II=25),
    weights=Weights(
        W_RR=0.20, W_CC=0.10, W_EE=0.10, W_TT=0.20,
        W_SS=0.15, W_AA=0.15, W_II=0.10,
    ),
    transparency=TransparencyClass.WHITE_BOX,
    provisional=True,
    notes=(
        "PROVISIONAL VALUES — pending multidisciplinary expert-panel scoring "
        "per Mahajan (2024) Ch 5.3. Defensive autonomous system; operates "
        "in second-scale latency window precluding in-flight oversight. "
        "Classed as white box because engagement rules are pre-programmed "
        "and inspectable. Ethical/legal compliance score reflects "
        "purely defensive use against incoming projectiles."
    ),
)


# ============================================================================
# SAMSUNG SGR-A1 -- PROVISIONAL; pending expert-panel scoring
# ============================================================================
# Korean DMZ sentry. Autonomous identify-and-engage capability though
# typically operated with human-in-the-loop for lethal engagement.
SGR_A1 = SystemFixture(
    id="sgr_a1",
    name="Samsung SGR-A1",
    system_type="Stationary Sentry Robot",
    manufacturer="Samsung Techwin (now Hanwha Aerospace)",
    year_of_service=2014,
    elements=Elements(RR=30, CC=20, EE=33, TT=22, SS=28, AA=27, II=35),
    weights=Weights(
        W_RR=0.20, W_CC=0.10, W_EE=0.20, W_TT=0.10,
        W_SS=0.15, W_AA=0.15, W_II=0.10,
    ),
    transparency=TransparencyClass.GLASS_BOX,
    provisional=True,
    notes=(
        "PROVISIONAL VALUES — pending multidisciplinary expert-panel scoring. "
        "Stationary border-zone sentry with auto-detect and optional auto-"
        "engage. Korean DMZ deployment context elevates Risk Level and "
        "Accountability Issues. Ethical/legal compliance score reflects "
        "armistice-zone constraints."
    ),
)


# ============================================================================
# KARGU-2 -- PROVISIONAL; pending expert-panel scoring
# ============================================================================
# Turkish loitering munition. UN Panel of Experts on Libya (2021) reported
# possible autonomous engagement of human targets in 2020.
KARGU_2 = SystemFixture(
    id="kargu_2",
    name="Kargu-2",
    system_type="Loitering Munition (Suicide Drone)",
    manufacturer="STM Defense Technologies",
    year_of_service=2019,
    elements=Elements(RR=38, CC=28, EE=40, TT=25, SS=32, AA=28, II=38),
    weights=Weights(
        W_RR=0.25, W_CC=0.10, W_EE=0.20, W_TT=0.10,
        W_SS=0.10, W_AA=0.15, W_II=0.10,
    ),
    transparency=TransparencyClass.BLACK_BOX,
    provisional=True,
    notes=(
        "PROVISIONAL VALUES — pending multidisciplinary expert-panel scoring. "
        "Loitering munition with autonomous terminal-phase engagement. UN "
        "Panel of Experts on Libya (S/2021/229) reported Kargu-2 may have "
        "engaged human targets autonomously in 2020. Highest accountability "
        "and ethical/legal scores in the baseline set. Classed as black box "
        "given closed-weight classifier and short engagement window."
    ),
)


# ============================================================================
# PHALANX CIWS -- PROVISIONAL; pending expert-panel scoring
# ============================================================================
# US Navy close-in weapon system. Defensive; millisecond-scale engagement
# against anti-ship missiles. The 1988 USS Vincennes Aegis incident (cited
# in Mahajan 2024 p.16 as cautionary case study) is in the broader system
# family.
PHALANX = SystemFixture(
    id="phalanx",
    name="Phalanx CIWS",
    system_type="Close-In Weapon System (Defensive)",
    manufacturer="Raytheon (originally General Dynamics)",
    year_of_service=1980,
    elements=Elements(RR=18, CC=22, EE=12, TT=14, SS=18, AA=18, II=20),
    weights=Weights(
        W_RR=0.15, W_CC=0.10, W_EE=0.10, W_TT=0.25,
        W_SS=0.15, W_AA=0.15, W_II=0.10,
    ),
    transparency=TransparencyClass.WHITE_BOX,
    provisional=True,
    notes=(
        "PROVISIONAL VALUES — pending multidisciplinary expert-panel scoring. "
        "Last-line defensive system against incoming anti-ship missiles. "
        "Millisecond-scale engagement; no in-flight human oversight possible "
        "by design. Classed as white box (deterministic rule-based)."
    ),
)


REGISTRY: dict[str, SystemFixture] = {
    MQ9_REAPER.id: MQ9_REAPER,
    IRON_DOME.id: IRON_DOME,
    SGR_A1.id: SGR_A1,
    KARGU_2.id: KARGU_2,
    PHALANX.id: PHALANX,
}


def get_fixture(system_id: str) -> SystemFixture:
    """Look up a fixture by its short id (e.g. 'mq9', 'iron_dome')."""
    key = system_id.strip().lower().replace("-", "_")
    if key not in REGISTRY:
        raise KeyError(
            f"Unknown system id '{system_id}'. Available: "
            f"{', '.join(sorted(REGISTRY.keys()))}"
        )
    return REGISTRY[key]


def list_fixtures() -> list[SystemFixture]:
    """Return all baseline fixtures in registry order."""
    return list(REGISTRY.values())
