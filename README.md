# Green Data Centre Site Selection — Northeast Brazil

> **Status: GitHub release candidate (25 November 2026). The analytical baseline remains provisional while the current ANA water layer and July-2026 CNUC geometry are being refreshed.**

## The question

Where in Northeast Brazil is large digital infrastructure most defensible when renewable-resource quality, grid infrastructure, telecom connectivity, cooling climate, water constraints, environmental limits, policy context and evidence uncertainty are considered together?

This project screens all **1,794 municipalities in Brazil's Northeast** using public official data. It is not a parcel-selection tool and it does not claim that a municipality has spare electrical capacity, available dark fibre, permitted industrial water or an immediately developable site.

## Why this project matters

Northeast Brazil combines exceptional wind and solar resources with rapidly growing interest in hyperscale and AI infrastructure. At the same time, the region illustrates a central infrastructure challenge: strong renewable potential and visible transmission assets do not automatically mean that a large new load can connect at the required time, place and scale.

The model therefore separates three things that are often collapsed into one number:

1. **Due-diligence gates** — requirements that a weighted score cannot override, such as project-level grid connection feasibility, water strategy, parcel legality and REDATA compliance.
2. **Evidence confidence** — how directly and recently each public dataset supports the screening result.
3. **Scenario attractiveness** — municipality-level relative scores for different data-centre strategies.

## Scenarios

The project evaluates four controlled decision scenarios rather than claiming one universal ranking:

- **Hyperscale AI** — grid and energy weighted most heavily.
- **Colocation / Digital Hub** — connectivity and grid dominate.
- **Renewable-First Compute** — energy resource and grid dominate.
- **Low-Water AI** — currently a **proxy only** until the final water layer is integrated.

The published weights are scenario assumptions, not empirical truths. A 1,500-run Monte Carlo sensitivity analysis perturbs those weights to measure rank stability.

## Data architecture

The screening model uses:

- **ANEEL SIGA** — generation assets and renewable pipeline context.
- **IBGE** — 2025 municipality boundaries and stable `CD_MUN` joins.
- **EPE** — existing/planned transmission lines and substations.
- **ONS** — operating substations and constrained-off renewable generation.
- **INPE/LABREN** — long-term solar-resource climatology.
- **Global Wind Atlas** — 100 m hub-height wind-resource statistics.
- **ANATEL** — fibre backhaul and endpoint-provider diversity.
- **INMET** — 1991–2020 climate normals, interpolated from resolved station coordinates.
- **ANA/SNIRH** — hydrological availability methodology; final municipality Q95 evidence pending endpoint extraction.
- **MMA/CNUC** — protected-area constraints; current model uses August 2025 geometry while the July 2026 refresh is queued.
- **MDIC / ZPE** — strategic and investment context from official web records.

## What the current model says

The current **provisional no-water** baseline identifies 17 Tier-A municipalities that remain robust across the four scenarios and 1,500 randomized weight perturbations.

The result is not simply a list of famous investment locations. **São Gonçalo do Amarante / Pecém** validates extremely strongly, but the model also surfaces less obvious renewable-grid corridors such as **Lajes, Caetité, Santa Luzia, Serra do Mel and São João do Piauí**. Conversely, a major connectivity hub such as **Fortaleza** does not automatically dominate the overall hyperscale ranking.

This is intentional: existing market activity is used as an external validation case, not as the target the model is forced to reproduce.

## A critical grid lesson

The model keeps **grid infrastructure strength** separate from **verified connection headroom**. A municipality can score highly for transmission proximity and strategic reinforcement while still face evidence of near-term connection constraints. This distinction is especially important in Pecém and Parnaíba.

## Water and REDATA

Water is intentionally not filled with a neutral or fabricated value. The final water framework distinguishes:

- hydrological availability;
- current demand pressure;
- permitted industrial supply;
- reclaimed-water potential; and
- facility-level Water Usage Effectiveness (WUE).

For REDATA-oriented projects, facility-level clean-energy and water-efficiency obligations are treated as due-diligence gates rather than municipality score bonuses.

## Reproducibility

The repository/release package is designed to include:

- source registry and provenance;
- municipality feature tables;
- scenario weights;
- deterministic MCDA scoring code;
- deterministic Monte Carlo sensitivity code;
- QA outputs;
- web-ready GeoJSON;
- candidate comparison tables; and
- an interactive decision-support dashboard.

## Current limitations

This is a municipality-level public-data screen. Final investment decisions still require parcel-level due diligence, utility studies, grid access approval, commercial carrier checks, geotechnical work, environmental licensing, water permitting, cooling design, tax/legal review and construction/logistics analysis.

The public release should remain labelled **provisional** until the current ANA water layer and July-2026 CNUC refresh are integrated and the model is rerun.
