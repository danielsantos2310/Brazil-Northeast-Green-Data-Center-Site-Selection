# Project Status — 25 November 2026 — v5

## Brazil Northeast Green Data Centre Site Selection

### Roadmap

- Step 01 — Foundation: **COMPLETE**
- Step 02 — Acquisition/provenance: **COMPLETE** for the planned source families.
- Step 03 — ANEEL generation: **COMPLETE**
- Step 04 — IBGE spatial foundation: **COMPLETE**
- Step 05 — EPE grid foundation: **COMPLETE**
- Step 06 — ONS operating-grid/curtailment context: **COMPLETE**
- Step 07 — Solar + wind resource: **COMPLETE**
- Step 08 — Connectivity: **COMPLETE**
- Step 09 — Climate + water: **PARTIAL** — climate complete with resolved station coordinates; ANA Q95 municipality integration remains.
- Step 10 — Environment: **COMPLETE / CURRENT** — official MMA/CNUC July-2026 geometry processed and propagated through the model.
- Step 11 — Suitability model: **PROVISIONAL v3** — climate + July-2026 environment complete; water deliberately not scored.
- Step 12 — Candidate/sensitivity: **PROVISIONAL v3** — rankings, 1,500-run sensitivity, Pareto, scenario dependence and external validation rerun.
- Step 13 — Website: **GITHUB RELEASE-CANDIDATE BUILD COMPLETE** — dashboard, web data and charts are in `website/`.
- Step 14 — Public release: **PROVISIONAL** — final analytical freeze still requires ANA water integration and one final rerun.

## Current baseline

All **1,794 Northeast municipalities** are represented. Current weighted dimensions are energy, grid strength, connectivity, climate/cooling, environment and strategic context. Water remains explicitly `NOT_SCORED`; no neutral value is imputed.

Four scenarios: Hyperscale AI; Colocation / Digital Hub; Renewable-First Compute; Low-Water AI proxy.

## Climate

All 74 core INMET station codes have resolved coordinates with provenance; seven retain relocation/coordinate-conflict flags. The exact-coordinate upgrade produced zero top-50 membership changes.

## Environment — July 2026

Official snapshot: `CNUC_2026_07`, acquired and processed through GitHub Actions.

- 732 municipalities with any CNUC overlap
- 258 intersecting Integral Protection areas
- 347 with >=10% overlap
- 213 with >=30% overlap
- 30 municipalities changed environmental constraint tier versus August 2025

Environment score: `1 - integral_protection_share - 0.35 × sustainable_use_share`, clipped to [0,1].

The refresh changed hundreds of lower/middle ranks but produced **zero top-50 membership changes** and **zero Tier-A entrances/exits** across all four scenarios.

## Sensitivity / robust candidates

Fresh 1,500-run Monte Carlo on the July-2026 environment baseline: **Tier A 17; Tier B 30; Tier C 75**.

Tier A: São Gonçalo do Amarante, Caetité, Santa Luzia, Milagres, Urandi, Lajes, Assú, Igaporã, Aquiraz, João Câmara, Serra do Mel, São João do Piauí, Campina Grande, Juazeiro, Ourolândia, Irecê, Bom Jesus da Lapa.

Exact Pareto validation across energy, grid, connectivity, climate and environment places **16/17 Tier-A municipalities on the non-dominated frontier**. Igaporã remains dominated by Caetité.

Pairwise top-50 overlap remains **27–39 municipalities**, confirming meaningful scenario dependence.

## Water — remaining analytical gate

ANA's official surface-water FeatureServer is reachable from GitHub Actions and exposes geometry plus `DISPQ95` (m³/s). A prior run retrieved the first 7,000 Northeast features before a transient HTTP 502. The downloader is now hardened with smaller pages, retry/backoff, page-size fallback, deterministic OBJECTID ordering and duplicate-ID QA.

Q95 will remain **hydrological availability evidence only** — not a water right, utility commitment, permitted withdrawal or cooling-water feasibility result.

## GitHub / web

Repository: https://github.com/danielsantos2310/Brazil-Northeast-Green-Data-Center-Site-Selection

The browser map ships the union of 162 municipalities that reach the top 100 in at least one scenario for performance. The analytical model still covers all 1,794 municipalities.

## Final analytical gate

Before freezing the ranking: complete ANA Q95 aggregation; build a defensible water evidence dimension; rerun all scenarios + 1,500-run sensitivity; rerun Pareto/scenario validation; regenerate website data; run final QA.

A high score means **deserves deeper engineering and commercial due diligence**, not construction-ready.