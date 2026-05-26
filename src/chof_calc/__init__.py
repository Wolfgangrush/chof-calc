"""
chof-calc — Quantifying Human Oversight for Autonomous Weapon Systems.

Operationalises the H equation from:
  Mahajan, R. R. (2024). What Balance Between Human Oversight and Machine
  Autonomy Is Necessary To Uphold Ethical Standards in Warfare, and How Can
  This Balance Be Legally Codified and Enforced. LLM Dissertation, Queen's
  University Belfast, School of Law.

The equation (H_v1, dissertation-faithful):

           1     N
  H = 100 - --- · Sigma (W_i * c_i)
          SUM_W  i=1

  where:
    i in {RR, CC, EE, TT, SS, AA, II}   (the seven CHOF elements)
    c_i in [1, 45]                      (element score)
    W_i in [0, 1]                       (element weight; SUM_W = 1)

Public API:
    chof_calc.HEquation           — the equation as a pure function
    chof_calc.Elements            — 7-element scaffolding + scoring bands
    chof_calc.Weights             — weight elicitation + validation
    chof_calc.TransparencyClass   — black / glass / white box
    chof_calc.systems             — baseline weapon-system fixtures

License: Apache-2.0
Citation: see CITATION.cff in the repository root.
"""

from chof_calc.elements import Element, Elements, RiskBand
from chof_calc.equation import HEquation, HResult
from chof_calc.transparency import TransparencyClass
from chof_calc.weights import Weights

__version__ = "0.1.0-alpha"
__all__ = [
    "Element",
    "Elements",
    "HEquation",
    "HResult",
    "RiskBand",
    "TransparencyClass",
    "Weights",
    "__version__",
]
