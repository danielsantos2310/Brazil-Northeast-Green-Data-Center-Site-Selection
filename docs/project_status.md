# Project Status — 24 November 2026 — v4

## Brazil Northeast Green Data Centre Site Selection

### Roadmap

- Step 01 — Foundation: COMPLETE
- Step 02 — Acquisition/provenance: COMPLETE for current planned source families; MDIC represented by dated official-web provenance because no structured download is published.
- Step 03 — ANEEL generation: COMPLETE
- Step 04 — IBGE spatial foundation: COMPLETE
- Step 05 — EPE grid foundation: COMPLETE
- Step 06 — ONS operating-grid/curtailment context: COMPLETE
- Step 07 — Solar + wind resource: COMPLETE
- Step 08 — Connectivity: COMPLETE
- Step 09 — Climate + water: PARTIAL — climate v2 complete with resolved station coordinates; ANA water spatial integration pending service extraction.
- Step 10 — Environment: PARTIAL — August-2025 CNUC geometry processed; July-2026 official refresh verified and automated refresh script prepared, but remote resource download remains blocked in the current environment.
- Step 11 — Suitability model: PROVISIONAL — v2 exact-coordinate climate baseline complete; water deliberately not scored.
- Step 12 — Candidate/sensitivity analysis: PROVISIONAL — deterministic scenario rankings, 1,500-run sensitivity, Pareto validation, scenario-dependence analysis and external-validation cases complete.
- Step 13 — Website: INTERNAL CHECKPOINT COMPLETE — authoritative unpublished folder `v2_climate_exactcoords_2026-11-24_final`; earlier website versions archived.
- Step 14 — Public release: HOLD — requires final water/CNUC rerun and explicit user approval.

## Current analytical baseline

All 1,794 Northeast municipalities are represented.

Current weighted dimensions: energy, grid strength, connectivity, climate/cooling, environment, strategic context. Water remains `NOT_SCORED`.

Four controlled scenarios:
- Hyperscale AI
- Colocation / Digital Hub
- Renewable-First Compute
- Low-Water AI proxy

The scoring architecture is explicitly separated into:
1. project/due-diligence gates;
2. evidence confidence; and
3. municipality attractiveness.

## Climate v2

All 74 core INMET station codes used by the normal-climate layer have resolved coordinates with provenance. Seven retain relocation/conflict flags. The climate update did not change top-50 membership in any scenario, showing strong stability of the leading candidate universe.

## Sensitivity and robust candidates

The deterministic 1,500-run Monte Carlo sensitivity analysis yields:
- Tier A: 17 municipalities
- Tier B: 29
- Tier C: 75
- not robust: 1,673

Tier A:
São Gonçalo do Amarante, Caetité, Santa Luzia, Milagres, Urandi, Lajes, Assú, Igaporã, Aquiraz, João Câmara, Serra do Mel, São João do Piauí, Campina Grande, Juazeiro, Ourolândia, Irecê, Bom Jesus da Lapa.

## Weight-independent validation

An exact Pareto test across energy, grid, connectivity, climate and environment — excluding strategic/ZPE context and all scenario weights — places 16 of the 17 Tier-A municipalities on the non-dominated frontier. Igaporã is the sole Tier-A exception and is dominated by Caetité in the current public-data feature table.

## Scenario dependence

Scenario rankings are related but materially different. Top-50 overlap ranges from 27 to 39 municipalities across scenario pairs. This validates the decision to expose scenario switching rather than publish one universal rank.

Examples of specialist behaviour:
- Santana do Matos: #12 Renewable-First vs #273 Colocation.
- Cabo de Santo Agostinho: #3 Colocation vs #94 Renewable-First.
- Parnaíba: #6 Colocation vs #81 current Low-Water proxy.

## External validation

The model does not simply reproduce investment announcements.
- São Gonçalo/Pecém validates strongly (#1 Hyperscale and Colocation) but retains EPE near-term access-risk evidence.
- Fortaleza is a connectivity benchmark but only #48 Hyperscale in the provisional model.
- Lajes is #6 Hyperscale without a strategic/ZPE bonus.
- Parnaíba and Suape are scenario-dependent rather than universal leaders.

## Water method

Preferred ANA source is the official surface-water availability FeatureServer containing `DISPQ95` geometry and values. The final water framework distinguishes hydrological availability, current demand pressure, permitted supply, reclaimed-water potential and facility WUE. No neutral water value is inserted.

REDATA water/clean-energy requirements are project-level gates, not municipality bonuses.

## Environment refresh

MMA confirms `CNUC_2026_07` as the current official conservation-unit release, updated 21 August 2026. The current numerical overlay remains the preserved August-2025 snapshot until the current geometry can be downloaded and processed.

## Website / publication control

Active website folder contains only:
- `v2_climate_exactcoords_2026-11-24_final`
- `Archive_PreFinal_Drafts`

Old root v1 files and the stale v2 draft were moved into the archive; nothing was deleted.

The v2 site passed internal structural QA:
- JavaScript syntax PASS
- all local references resolve
- 1,794 GeoJSON municipality features
- four scenario keys
- 100 records per top-100 scenario list
- 17 Tier-A records
- all Tier-A IDs resolve to map features

## Public-release gate

Do not publish until:
1. ANA Q95 evidence is spatially integrated;
2. July-2026 CNUC geometry is processed;
3. model and 1,500-run sensitivity are rerun;
4. final web assets are regenerated;
5. no legacy files are referenced; and
6. Daniel explicitly approves publication.
