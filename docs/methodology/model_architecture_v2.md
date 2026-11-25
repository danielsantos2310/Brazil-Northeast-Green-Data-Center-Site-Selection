# Model architecture v2 — Gates → Evidence confidence → Scenario attractiveness

## Why this architecture
A weighted average is not enough for infrastructure siting. A municipality can have excellent renewable resources while a specific project still fails because of grid connection, protected land, water strategy, or REDATA requirements.

The project therefore uses three layers:

### Layer 1 — Hard / due-diligence gates
Project-level conditions that cannot be compensated by a higher score elsewhere. Examples: REDATA WUE and clean-energy requirements, viable electrical connection pathway, parcel environmental compatibility, legally/operationally credible water strategy, and hyperscale-grade network redundancy.

### Layer 2 — Evidence confidence
Every dimension records whether the evidence is direct, inferred, old, municipality-level, planned, or otherwise uncertain. Missing/weak evidence is not converted into false precision.

### Layer 3 — Scenario attractiveness
Four transparent decision scenarios (Hyperscale AI, Colocation/Digital Hub, Renewable-first Compute, Low-water AI proxy) rank municipalities using documented weights. Water is currently absent and remaining weights are renormalized. The weights are controlled decision scenarios, not empirical truths.

## Current stress tests
- 1,500 lognormal weight perturbations per scenario (sigma=0.20; deterministic seed 20261124).
- Anti-circularity test: strategic/ZPE context weight forced to zero.
- EPE access-risk stress: 25% grid-component haircut for municipalities with documented Pecém/Parnaíba near-term access-risk evidence. This is a stress test, **not** a headroom estimate.

## Robustness tiers
Tier A requires median cross-scenario rank <=25, worst scenario p90 rank <=80, and mean top-50 frequency >=0.85. Tier B requires mean top-50 frequency >=0.50. Tier C requires mean top-decile frequency >=0.75. Others remain unclassified/not robust.

## Current v2 result
The exact-coordinate climate rerun preserves 17 Tier-A municipalities. Bom Jesus da Lapa enters Tier A and Aracati moves to Tier B. Top-50 membership is unchanged in all four scenarios relative to the earlier municipality-proxy climate model, indicating structural stability while still responding to improved evidence.

## Publication rule
The website must never present `score = certainty`. Every candidate page should expose the component scores, evidence confidence, hard-gate status, sensitivity/rank stability and unresolved due-diligence items.
