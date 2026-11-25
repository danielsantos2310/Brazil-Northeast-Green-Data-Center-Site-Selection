# Methodology update — Steps 07–12 (2026-11-24)

## Purpose
This update advances the Northeast Brazil green data-centre screening project from energy/grid foundations into resource quality, digital connectivity, climate, environmental constraints, integrated multi-criteria scoring and sensitivity analysis.

The unit of analysis remains the IBGE municipality (1,794 municipalities). Results are **screening evidence**, not parcel feasibility or investment advice.

## Step 07 — Solar and wind resource
### Solar
Source: INPE/LABREN, Atlas Brasileiro de Energia Solar, 2nd edition (2017).
Official source: https://labren.ccst.inpe.br/atlas_2017.html

Five national 0.1° point datasets were processed:
- Global Horizontal Irradiation (GHI)
- Direct Normal Irradiation (DNI)
- Diffuse irradiation
- Tilted-at-latitude irradiation
- PAR

For each municipality, LABREN grid points inside the IBGE polygon were summarized with annual mean, median, P10, P90, minimum and maximum. Monthly means were retained for GHI and tilted irradiation.

1,694 municipalities contained at least one LABREN grid centre. 100 small municipalities required a nearest-grid fallback. Fallback distance is retained explicitly. Fernando de Noronha is a major outlier (~361 km from the nearest grid point) and must be treated as low-confidence solar evidence.

### Wind
Source: Global Wind Atlas 4 municipality statistics already processed in the project.
Official source: https://globalwindatlas.info/en/download/gis-files

The `100m` designation is hub height, not assumed raster-cell resolution. The municipality table uses mean/median/P90/max wind speed and power density at 100 m.

### Preliminary resource indicators
Resource percentiles are exploratory only:
- solar resource: 75% annual GHI percentile + 25% seasonal-stability percentile
- wind resource: 65% mean power-density percentile + 35% mean wind-speed percentile
- hybrid resource: 50% solar + 50% wind

These are not final site-suitability scores.

## Step 08 — Connectivity
Source: ANATEL transport/backhaul data (2025 snapshot).
Official context: https://www.gov.br/anatel/pt-br/dados/infraestrutura/pert/pert

Connectivity is based primarily on provider diversity rather than binary fibre presence. Metrics include:
- fibre-backhaul status,
- unique endpoint provider count,
- endpoint link count,
- neighbouring municipalities connected,
- intersecting fibre lines/providers,
- nearest fibre-line distance,
- 2023–2025 continuity.

This does **not** prove dark-fibre availability, physical route independence, wavelength capacity, latency or commercial SLA.

## Step 09 — Climate (PROVISIONAL)
Source: INMET Normais Climatológicas 1991–2020.
Official source: https://portal.inmet.gov.br/normais

Variables used:
- compensated mean air temperature,
- mean wet-bulb temperature,
- mean maximum temperature,
- hottest monthly mean maximum,
- relative humidity,
- dew point.

The downloaded files did not include station coordinates. Station names were therefore matched to IBGE municipalities, and the municipality representative point was used as a station-location proxy. Five-nearest inverse-distance interpolation was then used across Northeast municipalities.

This layer is explicitly provisional and must be replaced with exact INMET station coordinates before final publication. Normals represent climatology, not heat-wave extremes.

## Step 09 — Water (PENDING SPATIAL JOIN)
Source: ANA/SNIRH surface-water availability.
Official spatial service:
https://portal1.snirh.gov.br/server/rest/services/dados_abertos/Disponibilidade_Hidrica_Superficial/FeatureServer/0

The downloaded CSV contains availability attributes but no geometry. The official service exposes polyline geometry and `DISPQ95` (m³/s), but bulk geometry extraction was unavailable in this processing environment.

No water value was fabricated or imputed. Water remains `NOT_SCORED_ANA_SPATIAL_JOIN_PENDING`.

Water availability will represent hydrological evidence only—not industrial abstraction rights, permits, reclaimed-water supply or cooling-water feasibility.

## Step 10 — Environment
Source snapshot: MMA/CNUC August 2025 polygon dataset.
Current portal: https://dados.mma.gov.br/dataset/unidadesdeconservacao

Municipality overlap was calculated in EPSG:5880 using the same projected municipality geometry as the percentage denominator. This avoids coastal/island percentages above 100%.

Metrics:
- total CNUC overlap,
- Proteção Integral overlap,
- Uso Sustentável overlap,
- UC count and constraint tier.

Environmental score for exploratory modelling applies a full penalty weight to integral-protection share and a softer 0.35 weight to sustainable-use share. This is municipality screening only: an entire municipality is **not** legally excluded merely because a protected area exists within it.

The final publication must refresh the layer to CNUC July 2026, which the MMA portal identifies as the current release.

## MDIC / ZPE context
Primary official page:
https://www.gov.br/mdic/pt-br/assuntos/zpe/zpe-criadas-e-projetos-aprovados

Because no official structured national download is provided, a dated structured reference was created from the official page. ZPE status is a strategic-context variable, not evidence of technical feasibility.

## Step 11 — Integrated model
Three analytical layers are kept separate:

1. constraints and warnings,
2. evidence confidence,
3. attractiveness scores.

### Energy score
45% hybrid natural-resource quality
25% operating wind/solar ecosystem
10% granted wind/solar pipeline context
5% operating renewable plant count
15% wind/solar operating balance

Pipeline capacity is intentionally low-weight because granted MW is not available firm supply.

### Grid-strength score
30% proximity to ONS ≥230 kV operating substation
20% proximity to EPE existing substation
15% voltage of nearest existing substation
15% density of ONS ≥230 kV substations within 50 km
10% existing ≥230 kV line intersection
10% planned reinforcement context

This score measures **infrastructure strength/proximity, not headroom**. `grid_headroom_verified` is false for every municipality because public topology data cannot prove spare connection capacity.

EPE's documented Pecém/Parnaíba near-term connection constraint is retained as a separate flag.

### Environment
Protected-area coverage reduces the environmental/land score, but municipality-level overlap does not become a blanket exclusion.

### Strategic context
Current version includes official ZPE evidence only. It is not a comprehensive tax/logistics/labour/land-cost model.

## Scenario model
Four controlled decision scenarios are used:
- Hyperscale AI
- Colocation / digital hub
- Renewable-first compute
- Low-water AI

Water is intentionally omitted from the current provisional scores and scenario weights are renormalized across the dimensions actually available. These scores must therefore be labelled `provisional_no_water`.

## Step 12 — Sensitivity
1,500 Monte Carlo weight perturbations were run per scenario using multiplicative lognormal noise (sigma 0.20) around the base non-water weights.

Two additional stress tests were run:
1. remove strategic/ZPE context entirely, to test circularity/market-validation bias;
2. apply a 25% grid-component haircut to Pecém and Parnaíba as a conservative EPE-access-risk sensitivity test.

The 25% haircut is **not an estimate of real spare capacity**.

Robustness results must be rerun after:
- ANA water geometry is joined,
- exact INMET station coordinates replace proxies,
- CNUC is updated to July 2026.

## Interpretation rule
A high score means:
> strong municipality-level public-data screening evidence under a stated scenario.

It does not mean:
> a parcel is available, connectable, permitted, financeable or construction-ready.
