# CHOF-Calc H_v2 — the narrative

The operational embodiment of RSH's QUB LLM dissertation as living, runnable software.
A reader should be able to reconstruct the intellectual arc from this file alone.

## Origin

The **H equation** comes from the QUB LLM (Law & Technology) dissertation, Sept 2024
(supervisor Dr Eugene Lim). It scores the **Human Oversight** required for an autonomous
weapon system across seven elements (Risk · Complexity · Ethics/Legal · Reliability ·
Safety · Accuracy · Accountability):

```
H = 100 - (1/ΣW) · Σ(W_i · c_i)
```

The MQ-9 Reaper baseline is the regression anchor. (The dissertation prints 75.35% on p.42;
the arithmetic actually yields **70.35%** — the tool reports the mathematically correct
value and documents the discrepancy rather than reproducing the typo.)

## The four execution gaps the dissertation acknowledged

1. Only MQ-9 simulated → **5 fixtures** now (MQ-9 · Iron Dome · SGR-A1 · Kargu-2 · Phalanx).
2. No sensitivity analysis → **Monte-Carlo** + **tornado** (`sensitivity_*`).
3. No historical backtest → **backtest harness** (Iran Air 655 · Kargu-2 Libya · Therac-25 · 737 MAX).
4. No empirical validation path → **AHP** (Saaty, CR<0.10) + **Delphi** panel aggregation (`weights_*`).

## The six theoretical moves beyond the cited literature (H_v1 → H_v2)

H_v1 was a single scalar. H_v2 is a five-output vector plus a layered architecture:

| Move | Module | What it adds |
|---|---|---|
| Transparency-class awareness | `transparency_classifier` + `h_modality` | black/glass/white box → which oversight modality (ex-ante / in-flight / ex-post) must attach |
| OODA latency mapping | `ooda_phase_mapper` | oversight-attention budget across Observe/Orient/Decide/Act; the "act" share collapses as the engagement window shrinks |
| Deployment-time evolution | `h_time_curve` | oversight weight varies pre-deployment / active / post-deployment |
| Pasquale counterfactual cost (T6) | `h_counterfactual` | expected harm at sub-100% oversight, as counterfactual-casualties-equivalent — the metric SIPRI/ICRC advocacy needs |
| Defense-in-depth (T4) | `defense_in_depth` | N independent oversight layers, each tuned to a distinct failure mode (Swiss-cheese) |
| Full-vector aggregation | `h_v2` | one call returns the whole H_v2 vector for a fixture + scenario |

## How it works

```python
from chof_calc.h_v2 import h_v2_for
h_v2_for("mq9")
# -> h_quantity 70.35, severity 'high', transparency 'glass_box',
#    h_modality {ex_ante 0.34, in_flight 0.33, ex_post 0.33},
#    h_latency_profile {observe .., orient .., decide .., act ..},
#    h_time_curve 1.0, h_counterfactual_cost ~14.8, defense_in_depth [3 layers]
```

Run `python demo.py` (or `python demo.py --jsonld`) for the full walkthrough across all fixtures.

## What it does NOT do

It is a **decision-support tool, not a definitive rule**. It does not replace human judgment
and it does **not make autonomous weapons safe** — it makes the *cost of choosing less-safe
options visible*. Every output is advisory; the human decides.

## Publication lineage

Dissertation (Sept 2024) → tool (this repo) → journal paper → UN GGE Geneva side-event.
