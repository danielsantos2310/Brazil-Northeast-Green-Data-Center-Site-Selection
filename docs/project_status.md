# Project Status — 25 November 2026 — v6

## Analytical screening status: COMPLETE

The municipality-level public-data screening is now complete across all planned evidence dimensions: energy, grid, connectivity, climate, environment, hydrology and strategic context.

### Roadmap

- Step 01 — Foundation: **COMPLETE**
- Step 02 — Acquisition / provenance: **COMPLETE**
- Step 03 — ANEEL generation: **COMPLETE**
- Step 04 — IBGE spatial foundation: **COMPLETE**
- Step 05 — EPE grid: **COMPLETE**
- Step 06 — ONS operating grid / curtailment: **COMPLETE**
- Step 07 — Solar + wind: **COMPLETE**
- Step 08 — Connectivity: **COMPLETE**
- Step 09 — Climate + hydrology: **COMPLETE for municipality screening**
- Step 10 — Environment: **COMPLETE / current July-2026 CNUC**
- Step 11 — Suitability model: **COMPLETE v4 water-integrated**
- Step 12 — Candidate + joint sensitivity: **COMPLETE v4**
- Step 13 — Interactive website: **COMPLETE v4**
- Step 14 — GitHub / Pages technical publication: **COMPLETE**.
- Step 15 — Portfolio communication package: **PREPARED**; portfolio case study and LinkedIn launch draft are versioned in `docs/`, but no external LinkedIn post has been published.
- Step 16 — Tier-A investment-screening deep dive: **IN PROGRESS**; v1 diligence gate matrix created and new SINISA / AdaptaBrasil / Cemaden evidence sources registered.

## Current robust shortlist

Tier A: 11 municipalities — São Gonçalo do Amarante, Juazeiro, Bom Jesus da Lapa, Parnaíba, Urandi, Paulo Afonso, Caetité, São João do Piauí, Brumado, Icó and Delmiro Gouveia.

Joint uncertainty tier counts: Tier A 11; Tier B 29; Tier C 69; not robust 1,685.

All 11 Tier-A candidates are Pareto non-dominated across energy, grid, connectivity, climate, environment and water.

## Water evidence

ANA/SNIRH Q95 pipeline succeeded end-to-end through GitHub Actions.

- 1,112 municipalities: direct mapped Q95 reach
- 682 municipalities: nearest-reach fallback
- fallback base decay: 25 km
- sensitivity range: 15–60 km
- all 11 Tier-A candidates: direct Q95 evidence

The score is hydrological-access evidence only. No municipality is marked as having verified water supply, water rights or permitted sustainable withdrawal.

## CNUC

Current environment snapshot: MMA/CNUC `CNUC_2026_07`. 732 municipalities have any overlap; 258 intersect Integral Protection areas.

## GitHub / Pages

Repository: https://github.com/danielsantos2310/Brazil-Northeast-Green-Data-Center-Site-Selection

Dashboard files are under `website/`, and repository-root `index.html` redirects to the dashboard for Pages publication.

## Remaining work is due diligence / communication, not missing screening data

Future improvements may add current basin demand-pressure evidence, flood/heat extremes, parcel land availability, utility offers, dark-fibre route independence, tariffs/taxes and investment-grade project economics. These are deeper diligence layers rather than blockers to the completed municipality screening.