# chof-calc

> **Quantifying Human Oversight for Autonomous Weapon Systems.**
> Operationalises the H equation from Mahajan (2024), *What Balance Between Human
> Oversight and Machine Autonomy Is Necessary To Uphold Ethical Standards in
> Warfare, and How Can This Balance Be Legally Codified and Enforced*, LLM
> Dissertation, Queen's University Belfast School of Law.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/Status-0.1.0--alpha-orange)](pyproject.toml)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](pyproject.toml)
[![Tests: 26 passing](https://img.shields.io/badge/Tests-26_passing-brightgreen)](tests/)

---

## TL;DR

`chof-calc` is an open-source research and policy tool that computes a
structured **Human Oversight (H) score** for an autonomous weapon system. Given
seven element scores and seven weights, the tool produces a percentage-valued
H score plus four enrichment outputs (modality · latency profile · time curve ·
counterfactual cost) that together form a defensible Article 36 weapons-review
assessment.

It is the **Tier 1** of a two-tier system. The companion **Tier 2** project
[`chof-kernel`](https://github.com/Wolfgangrush/chof-kernel) is the embedded
runtime kernel that enforces the H_required envelope inside an autonomous
system's flight stack.

Together they close the policy ↔ runtime loop: the commitment made at
procurement time (Tier 1) becomes enforceable at engagement time (Tier 2),
with cryptographically-signed audit trails linking the two for post-mission
Article 36 review.

---

## Table of contents

- [The story](#the-story)
- [The H equation](#the-h-equation)
- [The seven elements](#the-seven-elements)
- [The five baseline fixtures](#the-five-baseline-fixtures)
- [The H_v1 → H_v2 evolution](#the-h_v1--h_v2-evolution)
- [Documented correction to the published dissertation](#documented-correction-to-the-published-dissertation)
- [Install](#install)
- [Quickstart](#quickstart)
- [Python API](#python-api)
- [Use cases](#use-cases)
- [Architecture](#architecture)
- [Roadmap](#roadmap)
- [Comparison to existing frameworks](#comparison-to-existing-frameworks)
- [FAQ](#faq)
- [Development](#development)
- [Citation](#citation)
- [License](#license)
- [Author](#author)

---

## The story

In September 2024 the author submitted an LLM dissertation at Queen's
University Belfast's School of Law, on the
question of how meaningful human control over Autonomous Weapon Systems (AWS)
should be quantified and legally codified. The dissertation's core
contribution is the **H equation**: a Multi-Criteria Decision Analysis-based
weighted-sum that takes seven CHOF-derived element scores and returns a
percentage indicating the required level of human oversight for that system.

The dissertation received a Merit grade (65/100). The supervisor's feedback
identified four execution gaps that prevented a higher mark:

1. **Only one weapon system simulated** — the MQ-9 Reaper. Extending to a
   broader system class would have validated the equation's generality.
2. **No sensitivity analysis on the weights** — the seven weights are central
   to the H value but the dissertation did not test how robust the conclusion
   is to perturbations in weight assignment.
3. **No historical backtest** — the equation was never replayed against real
   incidents (Iran Air 655, Kargu-2 Libya, 737 MAX MCAS) to verify it would
   have produced reasonable scores at the moment of failure.
4. **No empirical validation pathway** — no protocol for converting expert
   panel judgments into element scores in a reproducible way.

This tool closes all four gaps simultaneously, and adds **six theoretical
moves beyond the cited literature** in the H_v1 → H_v2 evolution described
below.

The dissertation was deferred work for over a year before this tool began.
The author was unable to take the doctoral / academic path that the
dissertation pointed toward (UK defence-AI-ethics career) and returned to
litigation practice in India. This software is the operational counterpart
that ensures the underlying intellectual work survives as a citable artifact
regardless of where the author's career trajectory goes from here.

---

## The H equation

```
            1     N
  H = 100 − ─── · Σ (Wᵢ · cᵢ)
          ΣWᵢ   i=1
```

where:

- `i ∈ {RR, CC, EE, TT, SS, AA, II}` — the seven CHOF elements (defined below)
- `cᵢ ∈ [1, 45]` — element score on a Low / Medium / High band
- `Wᵢ ∈ [0, 1]` — element weight, with `ΣWᵢ = 1`

Interpretation:

- `H = 0%`     → the system requires no human oversight (full autonomy
                permissible)
- `H = 100%`   → the system requires complete human control over every
                decision (no autonomy permissible)
- `H = 75%`    → the system requires very high but not total human oversight

The tool maps H to a four-band severity:

| H band  | Severity   | Interpretation                                          |
|---------|------------|---------------------------------------------------------|
| 0–40    | LOW        | High autonomy permissible at this score                 |
| 40–70   | MEDIUM     | Moderate human oversight needed                         |
| 70–90   | HIGH       | High human oversight needed                             |
| 90–100  | CRITICAL   | Near-total human control required                       |

---

## The seven elements

Each element is scored on `[1, 45]` and falls into a band:

| Band     | Score range | Meaning                                                 |
|----------|-------------|---------------------------------------------------------|
| LOW      | 1–15        | Low risk for this dimension                             |
| MEDIUM   | 16–30       | Moderate risk                                           |
| HIGH     | 31–45       | High risk                                               |

| ID  | Element                       | What it captures                                                                                                |
|-----|-------------------------------|------------------------------------------------------------------------------------------------------------------|
| RR  | Risk Level                    | Potential for unintended civilian casualties and other severe consequences. Higher in combat-with-civilian zones |
| CC  | Operational Complexity        | Challenges of managing AWS in dynamic, unpredictable environments                                                |
| EE  | Ethical & Legal Compliance    | Alignment with International Humanitarian Law (distinction, proportionality, necessity)                          |
| TT  | Technological Reliability     | System predictability, robustness to environmental variation, malfunction rate                                   |
| SS  | Safety Concerns               | Risks to human life and operational-safety protocols beyond technical reliability                                |
| AA  | Accuracy of Targeting         | Ability to correctly identify and engage intended targets                                                        |
| II  | Accountability Issues         | Clarity of responsibility traceability when the system causes harm (the "moral crumple zone" risk)               |

Element scores must be set by a multidisciplinary expert panel per
Mahajan (2024) Ch 5.3: Military Strategists + Ethicists/Legal Scholars +
Engineers/Technologists + Human-Rights/Humanitarian Experts.

---

## The five baseline fixtures

| Fixture       | Type                       | Year | Transparency  | Status              | H_v2 |
|---------------|----------------------------|------|---------------|---------------------|------|
| **MQ-9 Reaper** | UCAV                     | 2007 | Glass box     | Dissertation-faithful | 70.35 % |
| Iron Dome       | Defensive air defence    | 2011 | White box     | Provisional         | 80.50 % |
| Samsung SGR-A1  | Stationary sentry        | 2014 | Glass box     | Provisional         | 72.05 % |
| Kargu-2         | Loitering munition       | 2019 | Black box     | Provisional         | 66.00 % |
| Phalanx CIWS    | Defensive close-in       | 1980 | White box     | Provisional         | 83.10 % |

**Only MQ-9 has dissertation-published values.** The other four fixtures
carry provisional values synthesised from open-source descriptions in the
dissertation's literature review and must be re-scored by a multidisciplinary
expert panel before any operational use. The CLI flags provisional fixtures
explicitly.

---

## The H_v1 → H_v2 evolution

This is the heart of the tool's contribution beyond the published
dissertation. The dissertation defined H as a scalar percentage. The tool
produces a **structured vector** with five outputs.

| Dimension                | H_v1 (dissertation, 2024) | H_v2 (this tool, 2026)                                                                            |
|--------------------------|---------------------------|---------------------------------------------------------------------------------------------------|
| Output shape             | Single scalar             | Five-output vector                                                                                |
| `H_quantity`             | The single scalar         | Kept as regression anchor                                                                         |
| `H_modality`             | None                      | NEW: transparency-class aware (black / glass / white box) → specifies which CHOF blocks apply     |
| `H_latency_profile`      | None                      | NEW: OODA-phase oversight distribution (Observe · Orient · Decide · Act)                          |
| `H_time_curve`           | Static                    | NEW: deployment-phase weight evolution (pre-deployment · active · post-deployment)                |
| `H_counterfactual_cost`  | None                      | NEW: Pasquale-derived expected-harm metric at sub-100% oversight                                  |
| MQ-9 reported value      | 75.35 % (typo)            | 70.35 % (mathematically correct, dissertation typo documented)                                    |
| 4 dissertation gaps      | Open                      | Closed (5+ system fixtures · sensitivity analysis · backtest harness · expert-panel scaffolding)  |
| AHP weight elicitation   | Manual only               | NEW: Saaty pairwise comparison wizard (Story S5)                                                  |
| Tier-2 runtime kernel    | None                      | NEW: companion repo `chof-kernel` enforces H at runtime via gate state machine                    |

### The six theoretical moves beyond cited literature

The dissertation cited 67 sources. The tool adds six theoretical moves that
go beyond those:

| #  | Move                                          | What it adds                                                                                                                                       |
|----|-----------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| T1 | AHP extended to oversight modalities          | Saaty (1980) pairwise comparison used for element weights AND for ex-ante vs in-flight vs ex-post modality selection                               |
| T2 | Russell uncertainty-preservation              | "Provably Beneficial AI" (Russell 2019) — AI's classification confidence feeds INTO H in real time. Low confidence → H spikes → operator-in-loop   |
| T3 | RL safe-exploration formalism                 | Bridges Santoni de Sio TRACKING condition to engineering literature (Garcia & Fernández 2015 · Berkenkamp 2017)                                    |
| T4 | Defense-in-depth layered architecture         | H outputs N independent oversight layers, not a single number. Reliability engineering pattern applied to AWS                                      |
| T5 | Bayesian dynamic-update hybrid                | Bayesian module ON TOP of MCDA baseline updates H dynamically with mission context. Dissertation rejected pure-Bayesian; this is hybrid           |
| T6 | Pasquale counterfactual-harm metric           | "Price of Autonomy" (Cambridge Handbook of AI 2022 Ch 14) — each percentage of automation gain has a quantified counterfactual harm cost          |

---

## Documented correction to the published dissertation

The dissertation reports `H_MQ9 = 75.35 %` on p.42 of the Simulation chapter.
The underlying weighted-sum value `29.65` is computed correctly in the
dissertation:

```
weighted_sum = 0.25·35 + 0.15·30 + 0.15·28 + 0.10·20 + 0.10·25 + 0.15·30 + 0.10·32
             = 8.75 + 4.50 + 4.20 + 2.00 + 2.50 + 4.50 + 3.20
             = 29.65   ✓
```

But the final subtraction step in the dissertation contains an apparent
arithmetic error:

```
H = 100 - 29.65
  = 70.35      ← mathematically correct
  ≠ 75.35      ← dissertation reports this (apparent typo)
```

This tool reports `H = 70.35 %` (the mathematically correct value) and emits
a `correction_note` field when invoked with the published value as input.

**The qualitative interpretation does not change.** Both 70.35% and 75.35%
fall in the HIGH oversight band, supporting the dissertation's conclusion
that "moderate to high human oversight is required for the MQ-9 Reaper."
The correction is in the displayed number, not in the meaning. This is the
first documented improvement in the H_v1 → H_v2 evolution.

This kind of public correction — finding and fixing one's own dissertation's
arithmetic at full transparency — is what we mean by "operationalising"
academic work: it forces every assumption through executable code and surfaces
discrepancies that paper-based review missed.

---

## Install

From PyPI (forthcoming):

```bash
pip install chof-calc
```

From source (today):

```bash
git clone https://github.com/Wolfgangrush/chof-calc
cd chof-calc
pip install -e ".[dev]"
```

Requires Python 3.10 or newer. Zero runtime dependencies (pure stdlib).
The dev install adds `pytest` for the test suite.

---

## Quickstart

### Reproduce the MQ-9 baseline

```bash
chof-calc assess --system mq9
```

Output (abridged):

```
==============================================================
  CHOF-CALC v0.1.0-alpha
==============================================================

SYSTEM ASSESSED
  Name:          MQ-9 Reaper
  Type:          Unmanned Combat Aerial Vehicle (UCAV)
  Manufacturer:  General Atomics Aeronautical Systems
  Year:          2007
  Transparency:  glass_box

ELEMENT SCORES (score band [1, 45])
  Element                         Score   Weight    Contribution
  RR -- Risk Level                35.00   0.2500    8.7500
  CC -- Operational Complexity    30.00   0.1500    4.5000
  EE -- Ethical & Legal Compliance28.00   0.1500    4.2000
  TT -- Technological Reliability 20.00   0.1000    2.0000
  SS -- Safety Concerns           25.00   0.1000    2.5000
  AA -- Accuracy of Targeting     30.00   0.1500    4.5000
  II -- Accountability Issues     32.00   0.1000    3.2000
  TOTAL                                   1.0000    29.6500

LIVE COMPUTATION (the equation walked through):
  H = 100 - [ (0.25 * 35) + (0.15 * 30) + ... ] / 1
  H = 100 - [ 8.75 + 4.50 + 4.20 + 2.00 + 2.50 + 4.50 + 3.20 ] / 1
  H = 100 - 29.65 / 1
  H = 100 - 29.6500
  H = 70.3500 %

RESULT
  H_quantity:    70.3500 %
  Severity:      [ HIGH ]     high human oversight needed

H_MODALITY (transparency-class aware oversight prescription)
  Class:                 glass_box
  CHOF blocks available: [1, 3, 4, 5, 6]
  In-flight supervision: feasible

DOCUMENTED CORRECTION TO PUBLISHED DISSERTATION
  Note: the dissertation reports H = 75.35% for this system.
  The computed value is H = 70.35%, a difference of 5.00 percentage
  points...
```

### List all baseline fixtures

```bash
chof-calc list
```

### Explain the equation

```bash
chof-calc explain
```

### JSON output for scripting

```bash
chof-calc assess --system mq9 --json
```

### Compare different systems

```bash
chof-calc assess --system kargu_2     # black box · provisional
chof-calc assess --system iron_dome   # white box · defensive
chof-calc assess --system phalanx     # white box · close-in defence
chof-calc assess --system sgr_a1      # glass box · sentry
```

---

## Python API

```python
from chof_calc import HEquation, Elements, Weights, TransparencyClass
from chof_calc.systems import MQ9_REAPER

# Compute the H score for an existing fixture
result = HEquation.compute(
    elements=MQ9_REAPER.elements,
    weights=MQ9_REAPER.weights,
    transparency=MQ9_REAPER.transparency,
)

print(result.h_quantity)          # 70.35
print(result.severity)            # OversightSeverity.HIGH
print(result.computation_trace)   # ["H = 100 - [...] / 1", ...]
print(result.element_contributions[Element.RR])  # 8.75

# Compute the H score for a custom system
custom_elements = Elements(RR=20, CC=18, EE=25, TT=15, SS=20, AA=22, II=28)
custom_weights = Weights(
    W_RR=0.20, W_CC=0.12, W_EE=0.18, W_TT=0.10,
    W_SS=0.12, W_AA=0.15, W_II=0.13,
)

result = HEquation.compute(
    elements=custom_elements,
    weights=custom_weights,
    transparency=TransparencyClass.GLASS_BOX,
)
```

---

## Use cases

The tool supports five distinct adoption pathways. Each is a separate adopter
cohort with separate value proposition.

### UC1 — Procurement gating

**Adopter:** Defence ministry procurement officer (DARPA · DRDO · DSTL · BWB
· IAF SIB).

**Use:** Standardised oversight rubric for choosing between vendor systems.
Vendor with H > 80% may be too operator-expensive to run; vendor with H < 30%
may fail Article 36 weapons review. The H equation creates a procurement
go/no-go band that procurement officers can defend in audit.

**Workflow:** vendor submits system specifications → multidisciplinary panel
scores 7 elements → tool produces H + modality + recommendation → procurement
officer compares like-for-like across competing bids.

### UC2 — Article 36 weapons-review backbone

**Adopter:** State legal-review office + ICRC.

**Use:** Every state party to Geneva Additional Protocol I (1977) must
legally review new weapons under Article 36. Most states have no standardised
methodology. The H equation can serve as the quantitative backbone of that
review, and ICRC can publish a methodology guide built on it.

**Workflow:** weapons reviewer assembles expert panel → panel scores
elements → tool produces H + modality → reviewer attaches the audit-grade
PDF as part of the formal review. The Tier 2 `chof-kernel` audit logs are
admissible as compliance evidence.

### UC3 — Treaty verification (UN GGE)

**Adopter:** UN Office for Disarmament Affairs + UN GGE on Lethal Autonomous
Weapons delegates.

**Use:** Signatory states publish H-scores for declared AWS. Public scores
create a transparency norm that strengthens emerging governance regimes.
Even non-signatory disclosure is a confidence-building measure.

**Workflow:** state authority computes H using the standardised tool → exports
JSON-LD treaty-verification format → publishes to UN repository → other
states can verify the computation independently.

### UC4 — NGO benchmarking + insurance underwriting

**Adopter:** SIPRI · ICRC · Article 36 · Human Rights Watch · insurance
industry.

**Use:** NGOs grade real-world AWS deployments by H-score and publish
league tables. Insurance industry uses the H-score as actuarial input to a
no-fault risk pool — the model the French Cour de cassation adapted from
the Badinter Law (1985) for road traffic, and which Monot-Fouletier
(*Cambridge Handbook of AI* 2022 Ch 12) proposes for autonomous vehicles.
The same model applied to AWS gives a compensation-fund framework that
internalises algorithmic risk.

### UC5 — Embedded compliance + export-control gating

**Adopter:** Defence prime ethics teams (Anduril · Shield AI · Palantir ·
Thales · BAE · Lockheed · Leonardo) and export-control agencies (UK ECJU ·
US BIS · Wassenaar Arrangement signatories).

**Use:** Defence primes integrate the Tier-2 `chof-kernel` into their flight
stacks for defensible Article 36 compliance posture. Export-control agencies
add H-score to the dual-use Goods Checker decision tree to flag high-
autonomy low-oversight systems for additional licensing scrutiny.

**Note:** This is the slowest-converting adoption channel. The
[BMAD plan](BMAD-PLAN.md) explicitly positions defence-prime engagement at
the END of the outreach cascade, AFTER academic publication + SIPRI/ICRC
methodology adoption + UN GGE side-event presentation have earned the
compliance-pressure authority that makes Stanford-PhD-staffed ethics
teams engage.

---

## Architecture

```
chof-calc/
├── pyproject.toml                     ← hatchling build · zero runtime deps
├── README.md                          ← this document
├── LICENSE                            ← Apache 2.0
├── NOTICE.md                          ← academic identity · BCI Rule 36 firewall
├── BMAD-PLAN.md → ../                 ← (parent project plan, separate folder)
├── src/chof_calc/
│   ├── __init__.py                    ← public API
│   ├── elements.py                    ← 7-element scaffolding + scoring bands
│   ├── weights.py                     ← weight validation (sum-to-1)
│   ├── equation.py                    ← HEquation.compute pure function · HResult
│   ├── transparency.py                ← black / glass / white box + CHOF block map
│   ├── cli.py                         ← argparse CLI
│   └── systems/
│       ├── __init__.py                ← fixture registry
│       └── fixtures.py                ← 5 baseline weapon systems
└── tests/
    ├── test_equation.py               ← math + validators (10 tests)
    ├── test_fixtures.py               ← fixture registry (10 tests)
    └── test_mq9_regression.py         ← Gate 1 regression anchor (6 tests)
```

### Pure-function design

The H equation is implemented as a pure function in `equation.py`. The
`HEquation.compute()` method takes immutable inputs (frozen dataclasses for
`Elements` and `Weights`) and returns an immutable `HResult`. There is no
hidden state, no global configuration, no I/O in the math layer. This makes
the math:

- **Reproducible** — same inputs always produce same outputs
- **Auditable** — every contribution to H is decomposed in
  `result.element_contributions` and `result.computation_trace`
- **Embeddable** — the math layer is reusable from the Tier-2 `chof-kernel`
  C++/Rust port via shared algorithm specification

### Transparency-class modality

The `TransparencyClass` enum has three values: `BLACK_BOX`, `GLASS_BOX`,
`WHITE_BOX`. Each carries:

- `cohf_blocks` — list of CHOF blocks (Verdiesen et al. 2020 Fig 4.2) where
  oversight can structurally attach for this class
- `supports_in_flight_supervision` — boolean indicating whether real-time
  human intervention is physically feasible
- `recommended_modality` — human-readable prescription string

This is the H_v2 modality output that solves the dissertation's gap where
H_v1 prescribed the same oversight regardless of system architecture.

---

## Roadmap

The full sprint plan lives in `BMAD-PLAN.md` of the parent project. v0.1.0-
alpha ships Stories S1, S2, S3, S7, S11, and the seed of S20.

### Shipped in v0.1.0-alpha (this release)

- [x] **S1** Core H_quantity pure function + 7-element scaffolding
- [x] **S2** Weight elicitation (manual + sum-to-1 validator)
- [x] **S3** Five baseline weapon-system fixtures
- [x] **S7** CLI interface (`assess` / `list` / `explain` / `version`)
- [x] **S11** Transparency-class classifier + H_modality output
- [x] **S20-seed** Dissertation lineage embedded in README + NOTICE
- [x] **Gate 1** MQ-9 regression test passes (70.35 % ± 0.01)
- [x] **Documented correction** apparent dissertation arithmetic typo flagged

### Forthcoming (Tier 1 build cadence)

- [ ] **S4** Monte Carlo sensitivity + tornado diagrams
- [ ] **S5** AHP pairwise comparison wizard (Saaty 1980 method)
- [ ] **S6** Historical backtest harness (Iran Air 655 · Kargu-2 Libya ·
       Therac-25 · 737 MAX)
- [ ] **S8** FastAPI + Streamlit web frontend
- [ ] **S9** Sphinx documentation site + Jupyter examples
- [ ] **S10** Journal paper draft (target: *AI & Ethics* / *Minds & Machines*
       / *Journal of International Humanitarian Legal Studies*)
- [ ] **S12** OODA-phase latency mapper (H_latency_profile output)
- [ ] **S13** Russell uncertainty-preservation integration
- [ ] **S14** Defense-in-depth layered architecture output
- [ ] **S16** Pasquale counterfactual-harm metric (H_counterfactual_cost)
- [ ] **S19** JSON-LD treaty-verification export schema
- [ ] **S20** Full narrative-in-app (Streamlit About + Sphinx site sections)

### Tier 2 — separate repository

The companion **embedded oversight kernel** ships in
[`chof-kernel`](https://github.com/Wolfgangrush/chof-kernel), already shipping
v0.1.0-alpha as a Python reference. The C++/Rust port for ROS2 / PX4 /
ArduPilot integration is targeted Q2-Q3 2027 after this Tier-1 project earns
academic authority through journal publication and NGO methodology adoption.

---

## Comparison to existing frameworks

| Framework                                                      | Quantitative? | AWS-specific? | Transparency-aware? | Backtest? | Public tool? |
|----------------------------------------------------------------|---------------|---------------|---------------------|-----------|--------------|
| DoD Directive 3000.09 (2023) "Responsible · Equitable · ..."   | No            | Yes           | No                  | No        | No           |
| EU AI Act Article 14 (2024) — Human oversight requirement      | No            | No (military exempt) | No           | No        | No           |
| UK DSIT Pro-Innovation 5 principles (2023)                     | No            | No            | No                  | No        | No           |
| ICRC Article 36 Guide (multiple editions)                      | No            | Yes           | No                  | No        | No           |
| Verdiesen et al. (2020) CHOF                                   | No            | Yes           | No                  | No        | No           |
| Santoni de Sio & van den Hoven (2018) Tracking + Tracing       | No            | Yes           | No                  | No        | No           |
| **chof-calc (this tool)**                                      | **Yes**       | **Yes**       | **Yes**             | **In progress (S6)** | **Yes (Apache 2.0)** |

The tool is the first public, audit-grade, quantitative operationalisation of
Meaningful Human Control for AWS. That is the wedge.

---

## FAQ

**Q: Is this tool legal advice?**
No. This is decision-support software, not legal advice. See `NOTICE.md` §3-4
for the BCI Rule 36 and decision-support-not-rule framing.

**Q: Can I use this tool in a real Article 36 weapons review?**
Yes, with two caveats. (a) The output is one input among many; expert
judgment remains primary. (b) Only the MQ-9 fixture has dissertation-
published values; the other four require expert-panel scoring before
operational use.

**Q: Why does the tool report 70.35% for the MQ-9 when the dissertation says
75.35%?**
The dissertation's published value of 75.35% contains an apparent arithmetic
typo in the final subtraction step (the weighted-sum 29.65 is correct, but
100 − 29.65 = 70.35, not 75.35). The tool reports the mathematically correct
value. See the "Documented correction" section above.

**Q: Why are four fixtures provisional?**
The dissertation only scored the MQ-9. The other four (Iron Dome · SGR-A1 ·
Kargu-2 · Phalanx) carry provisional values synthesised from open-source
descriptions and require a multidisciplinary expert panel to score before
operational use.

**Q: Why two repos (chof-calc + chof-kernel)?**
Different release cadence (Tier 1 ships first), different user audience
(policy researcher vs defence integrator), different future-licensing
options (chof-kernel may add commercial integration support later), and
different export-control disclosure scope.

**Q: Why Apache 2.0 instead of MIT or GPL?**
Apache 2.0 includes patent-grant language that protects defensive uses and
is compatible with integration into proprietary autonomous-systems flight
stacks. MIT lacks the patent grant; GPL would prevent industry integration.

**Q: Does this tool support [my favourite weapon system]?**
The CLI ships with 5 baseline fixtures. Adding a new system is a one-file
contribution to `src/chof_calc/systems/`. See `CONTRIBUTING.md`
(forthcoming) for the schema.

**Q: Can the tool be used for non-military autonomous systems (e.g.
medical robotics, autonomous vehicles)?**
The math layer is domain-neutral. The seven CHOF elements are AWS-specific
but the equation structure transfers. A future fork might rename to
`chof-calc-medical` etc. with sector-specific element semantics. PRs welcome.

---

## Development

### Run tests

```bash
pip install -e ".[dev]"
pytest -v
```

26 tests across 3 files. Test runtime ≈ 0.03 seconds.

### Code style

PEP 8. No formatter enforced yet; `black` and `ruff` will be added before
v0.2. Type hints used throughout but `mypy` not yet in CI.

### Contributing

Contributions welcome:

- **New baseline fixtures** — add a `SystemFixture` to
  `src/chof_calc/systems/fixtures.py` with proper provenance notes
- **New test scenarios** — extend `tests/test_fixtures.py`
- **Documentation** — Sphinx site is forthcoming (Story S9); contributions to
  the existing markdown are welcome via PR
- **Translation** — the tool will be useful to non-Anglophone policy bodies
  (UN, ICRC). i18n via gettext is on the backlog

See `CONTRIBUTING.md` (forthcoming) for full guidelines.

### Architectural conventions

- The math layer is pure-function only. No I/O, no globals, no hidden state.
- Element scores and weights are validated at construction time (frozen
  dataclasses with `__post_init__` validation).
- The CLI is a thin layer over the Python API; everything the CLI does is
  accessible programmatically.
- JSON outputs follow a stable schema (Story S19 will formalise as JSON-LD).

---

## Citation

If you use `chof-calc` in research, please cite both the tool and the
underlying dissertation:

```bibtex
@software{mahajan-chof-calc-2026,
  author       = {Mahajan, Rushikesh R.},
  title        = {chof-calc: Quantifying Human Oversight for Autonomous
                  Weapon Systems},
  year         = 2026,
  version      = {0.1.0-alpha},
  url          = {https://github.com/Wolfgangrush/chof-calc},
  note         = {Operationalises the H equation from Mahajan (2024)
                  QUB LLM Dissertation. DOI pending Zenodo.},
}

@thesis{mahajan-2024-dissertation,
  author       = {Mahajan, Rushikesh R.},
  title        = {What Balance Between Human Oversight and Machine
                  Autonomy Is Necessary To Uphold Ethical Standards in
                  Warfare, and How Can This Balance Be Legally Codified
                  and Enforced},
  type         = {LLM Dissertation},
  institution  = {Queen's University Belfast, School of Law},
  year         = 2024,
  month        = sep,
}
```

---

## License

Apache License 2.0. See [`LICENSE`](LICENSE) for the full text and
[`NOTICE.md`](NOTICE.md) for:

- Academic-identity declaration
- Queen's University Belfast attribution
- wolfgang_rush publishing-handle disclosure
- Bar Council of India Rule 36 firewall
- Dual-use disclosure
- Decision-support-not-rule clause
- Foundational-literature attribution

---

## Author

**Rushikesh Ravindra Mahajan** — LLM Law and Technology, Queen's University Belfast (2024).

Published as **wolfgang_rush**, an open-source brand for legal-technology
software. See [`NOTICE.md`](NOTICE.md) for the relationship between the two
identities.

Acknowledgments to Ilse Verdiesen, Filippo Santoni
de Sio, and Virginia Dignum (2020) for the CHOF framework that the equation
operationalises; to Vincent Boulanin (SIPRI 2020) and Michael Horowitz &
Paul Scharre (CNAS 2015) for the Meaningful Human Control literature.

---

**Companion repo:** [`chof-kernel`](https://github.com/Wolfgangrush/chof-kernel)
— the Tier-2 embedded oversight kernel.
