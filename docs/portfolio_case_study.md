# Portfolio Case Study — Northeast Brazil Green Data Centre Site Selection

## Overview

A reproducible geospatial decision-support project screening **1,794 municipalities across Northeast Brazil** for green data-centre development.

The model combines evidence across renewable energy, grid infrastructure, connectivity, climate, protected areas, hydrology and strategic context. It is designed as a **due-diligence funnel**, not as a claim that a municipality or parcel is construction-ready.

## Problem

Data-centre site selection is a multi-constraint infrastructure problem. Renewable resources, grid access, fibre, cooling conditions, environmental constraints and water all matter, but the available public datasets measure different things.

The project therefore keeps key distinctions explicit:

- transmission proximity is not spare connection capacity;
- renewable pipeline MW is not firm available supply;
- fibre-provider count is not physical route redundancy;
- ANA Q95 is not a water permit;
- municipality protected-area overlap is not parcel-level legality;
- a high municipality score is not an investment-grade site decision.

## Evidence stack

Primary sources include **IBGE, ANEEL, EPE, ONS, INPE/LABREN, Global Wind Atlas, ANATEL, INMET, ANA/SNIRH, MMA/CNUC and MDIC/ZPE**.

The final model evaluates seven dimensions:

1. Energy
2. Grid
3. Connectivity
4. Climate
5. Environment
6. Water
7. Strategic context

## Method

### Spatial processing

Source layers are normalized to the 1,794-municipality Northeast Brazil geography using geospatial joins, proximity calculations and municipality-level aggregation.

### Four strategic scenarios

The model tests:

- Hyperscale AI
- Colocation / Digital Hub
- Renewable-first Compute
- Water-resilient AI

Each scenario changes the weights placed on the seven evidence dimensions.

### Water integration

The final v4 model integrates official ANA/SNIRH Q95 surface-water evidence.

- **1,112 municipalities** directly intersect a mapped Q95 reach.
- **682 municipalities** use nearest-reach fallback evidence.
- Base fallback distance scale: **25 km**.
- Sensitivity range: **15–60 km**.
- All final Tier-A municipalities have **direct local Q95 evidence**.

### Robustness

The final shortlist is tested with **1,500 Monte Carlo runs per scenario**, with randomized scenario weights and uncertainty in the water fallback-distance rule.

A six-dimension Pareto analysis is also used across energy, grid, connectivity, climate, environment and water.

## Final result

The v4 water-integrated screening produces:

- **Tier A: 11**
- **Tier B: 29**
- **Tier C: 69**
- **Not robust: 1,685**

Final Tier-A municipalities:

1. São Gonçalo do Amarante, CE
2. Juazeiro, BA
3. Bom Jesus da Lapa, BA
4. Parnaíba, PI
5. Urandi, BA
6. Paulo Afonso, BA
7. Caetité, BA
8. São João do Piauí, PI
9. Brumado, BA
10. Icó, CE
11. Delmiro Gouveia, AL

All 11 are Pareto non-dominated across the six core dimensions and all 11 have direct mapped ANA Q95 evidence.

## Why water mattered

Before ANA hydrology was integrated, Tier A contained 17 municipalities.

After water became real evidence, the shortlist contracted to 11. Five municipalities entered the final Tier-A set with stronger hydrological evidence:

- Parnaíba
- Paulo Afonso
- Brumado
- Icó
- Delmiro Gouveia

This is an important model result: missing evidence was allowed to change the decision instead of being replaced with artificial neutrality.

## Reproducibility

The repository contains:

- official-source acquisition code;
- spatial-processing pipelines;
- scoring code;
- Monte Carlo sensitivity analysis;
- Pareto validation;
- processed reviewer-facing outputs;
- source registry and methodology;
- GitHub Actions refresh workflows;
- an interactive Leaflet/GeoJSON dashboard.

The ANA hydrological-access table was independently reproduced in GitHub Actions, with workflow and local scores matching to floating-point precision.

## Interactive dashboard

The browser dashboard provides:

- scenario filtering;
- a contender map;
- Tier-A profiles;
- multidimensional evidence charts;
- robustness visualisations;
- water-integration tier transitions;
- explicit due-diligence warnings.

For browser performance, the map contains the **190 municipalities appearing in at least one scenario's top 100**. The analytical model itself covers all 1,794 municipalities.

## Skills demonstrated

**Data / Analytics:** Python, pandas, GeoPandas, spatial analysis, feature engineering, MCDA, Monte Carlo sensitivity analysis, Pareto analysis, QA and provenance.

**Engineering:** reproducible pipelines, Git, GitHub, GitHub Actions, structured data workflows and versioned outputs.

**Frontend / Communication:** HTML, CSS, JavaScript, Leaflet, GeoJSON, interactive visualisation and executive decision communication.

## Next real-world diligence phase

A real investment process would next validate:

1. utility load-flow studies and connection offers;
2. firm/additional renewable-energy procurement;
3. water rights, utility supply and reclaimed-water options;
4. parcel-level environmental, flood, title and geotechnical constraints;
5. independent physical fibre routes;
6. cooling architecture, WUE/PUE and extreme-heat resilience;
7. taxes, tariffs, construction cost, workforce and project economics.

The 11 Tier-A municipalities would then be reduced to approximately **3–5 investment-screening finalists**.

## Links

Repository: https://github.com/danielsantos2310/Brazil-Northeast-Green-Data-Center-Site-Selection

Interactive dashboard: https://danielsantos2310.github.io/Brazil-Northeast-Green-Data-Center-Site-Selection/
