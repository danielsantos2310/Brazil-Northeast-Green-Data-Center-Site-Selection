# Step 16 — Tier-A Investment-Screening Deep Dive

**Status:** PUBLIC-DATA DEEP DIVE COMPLETE; EXTERNAL DILIGENCE PENDING  
**Baseline:** v4 water-integrated municipality screening · 25 November 2026

## Objective

Step 16 converts the 11 Tier-A municipalities from a regional attractiveness shortlist into an explicit due-diligence funnel.

This phase does **not** create another blended attractiveness score. It introduces blocking gates and evidence-gap resolution.

## Tier-A starting set

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

## Gate philosophy

Every candidate still has four universal unverified external-diligence gates:

- utility connection/headroom;
- permitted industrial water supply / water rights;
- independent physical carrier routes;
- parcel-level feasibility.

The municipality model is evidence for where to investigate first. It cannot close those gates.

## Initial public-data study bands

The deterministic Step-16 gate-matrix builder uses the final v4 evidence only.

### P1 — ADVANCE FIRST

Criteria:
- no EPE near-term access-risk flag;
- <10% municipality-level CNUC overlap;
- at least 5 recorded fibre providers;
- water score >=0.40;
- climate score >=0.45.

**Initial P1 queue:**
- Juazeiro, BA
- Bom Jesus da Lapa, BA
- Urandi, BA
- Brumado, BA
- Icó, CE

This is a **study-priority queue, not a final investment shortlist**.

### P2 — STRATEGIC CONDITIONAL

- São Gonçalo do Amarante, CE
- Parnaíba, PI

Both remain strategically important but carry an EPE near-term grid-access risk flag. Utility access/headroom is therefore an early blocking study.

### P3 — TARGETED RISK RESOLUTION

- Paulo Afonso, BA — material municipality CNUC overlap; weaker local wind/solar ecosystem.
- Caetité, BA — comparatively weak hydrological score and limited provider depth despite excellent grid/renewable/climate evidence.
- São João do Piauí, PI — challenging cooling-climate screen and limited provider depth.
- Delmiro Gouveia, AL — material municipality CNUC overlap, limited provider depth and weaker renewable-ecosystem score.

## New Step-16 evidence sources

### SINISA 2025 — Water supply

Use municipal water-service information and indicators to identify provider, coverage, production/distribution context, losses and operational indicators where reported.

Public-service capacity is not industrial allocation and does not prove that a data centre can obtain the required volume.

### SINISA 2025 — Stormwater

Use municipal drainage and reported flood-risk indicators as a first municipal-scale flood-context layer. This does not replace parcel floodplain/hydraulic modelling.

### AdaptaBrasil MCTI — Cities panel

Use municipal indicators for climate hazards, exposure and vulnerability, prioritising floods/flash floods/urban flooding, drought, heat-related risk where available, and water-system climate risk.

### Cemaden — Integrated Drought Index (IIS)

Use recent monthly drought conditions to distinguish long-term hydrological evidence (ANA Q95) from current/near-term drought stress.

## Reproducible code

`src/validation/build_tierA_diligence_gate_matrix.py`

Planned canonical output:

`data/processed/step16_tierA_diligence_gate_matrix_v1_2026-11-25.csv`

## Next execution sequence

1. Produce and validate the Tier-A gate matrix.
2. Add SINISA 2025 water-service evidence for all 11.
3. Add SINISA stormwater / municipal flood context.
4. Add AdaptaBrasil climate-risk indicators.
5. Add recent Cemaden IIS drought context.
6. Reclassify study bands without inventing private utility/fibre evidence.
7. Identify 3–5 candidates suitable for external commercial/engineering diligence.
8. Only after external diligence: parcel screening and investment-grade economics.

## Decision rule

A municipality can move forward because public evidence is strong enough to justify further spending.

It cannot be declared investment-ready until the blocking external gates are independently verified.

## Step-16 outcome

The public-data deep dive has narrowed the next external-diligence spend to five municipalities:

1. Bom Jesus da Lapa, BA
2. Brumado, BA
3. Juazeiro, BA
4. São Gonçalo do Amarante / Pecém, CE
5. Urandi, BA

Parnaíba, PI is the first reserve challenger.

This does not replace or alter the v4 Tier-A set. It is a deeper diligence queue. See `docs/step16_external_diligence_brief.md` and `data/processed/step16_external_diligence_shortlist_v1_2026-11-25.csv`.
