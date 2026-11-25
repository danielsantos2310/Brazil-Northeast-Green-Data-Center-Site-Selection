# Northeast Brazil Green Data Centre Site Selection

**A reproducible public-data screening framework for comparing 1,794 municipalities across energy, grid, connectivity, climate, environment, hydrology and strategic context.**

[Open the interactive dashboard](https://danielsantos2310.github.io/Brazil-Northeast-Green-Data-Center-Site-Selection/)

> **Release: v4 water-integrated municipality screening — 25 November 2026.** The model is complete as a regional public-data screening tool. It is **not** a parcel-level investment recommendation and does not replace utility connection studies, water rights, environmental licensing, carrier-route validation or engineering due diligence.

## Executive result

The final public-data screening produces **11 Tier-A robust candidates** after 1,500 joint uncertainty runs per scenario:

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

All 11 have **direct local ANA Q95 intersections** and all 11 are **Pareto non-dominated across six core dimensions**: energy, grid, connectivity, climate, environment and water.

### What changed when water became real evidence?

Before ANA hydrology was integrated, Tier A contained 17 municipalities. Water integration contracted the shortlist to 11 and introduced five locations with stronger hydrological evidence: **Parnaíba, Paulo Afonso, Brumado, Icó and Delmiro Gouveia**. Eleven previous Tier-A municipalities moved below Tier A.

This is a feature, not a defect: previously missing evidence is allowed to change the decision instead of being filled with a fake neutral score.

## Why this project is different

- **Grid infrastructure is not treated as grid headroom.** EPE/ONS proximity is scored separately from documented access-risk evidence.
- **Renewable pipeline MW is not treated as available supply.** Operating ecosystem and granted pipeline are separated.
- **Fibre presence is not treated as route diversity.** ANATEL provider diversity is evidence, not an SLA or dark-fibre guarantee.
- **Q95 is not treated as a water permit.** ANA hydrology is regional screening evidence only.
- **Municipality rank is not treated as parcel feasibility.** CNUC and other constraints remain hard due-diligence gates at site level.
- **Weights are not assumed to be truth.** Scenario weights are perturbed and the water fallback method is sensitivity-tested.

## Evidence stack

| Dimension | Primary sources | What is measured | What is explicitly *not* claimed |
|---|---|---|---|
| Energy | ANEEL SIGA, INPE/LABREN, Global Wind Atlas | operating clean-energy ecosystem, pipeline context, solar/wind resource | available firm power or contracted clean supply |
| Grid | EPE, ONS | transmission/substation infrastructure, operating grid context | spare MW / connection approval |
| Connectivity | ANATEL | fibre backhaul, endpoint-provider diversity | dark fibre, independent physical paths, SLA |
| Climate | INMET 1991–2020 normals | cooling-relevant climatology from 74 resolved station codes | extreme-weather design basis |
| Environment | MMA/CNUC July 2026 | protected-area overlap and Integral Protection exposure | parcel legality or licence outcome |
| Water | ANA/SNIRH Q95 | hydrological availability/access evidence | water right, utility supply, permitted sustainable withdrawal |
| Strategic | MDIC/ZPE + documented market context | policy/cluster context | substitute for physical feasibility |

## Water methodology

ANA's official surface-water availability geometry provides `DISPQ95` (m³/s).

- **1,112 municipalities** intersect at least one mapped Q95 reach directly.
- **682 municipalities** do not; for those, the model uses the nearest mapped ANA reach and a transparent distance-decay rule.
- Base fallback formula: `nearest Q95 percentile / (1 + distance_km / 25)`.
- The sensitivity model samples the decay scale **log-uniformly from 15–60 km** rather than trusting the 25 km base assumption.
- Crucially, **all 11 Tier-A municipalities have direct intersections**, so the Tier-A result is not being driven by the fallback-distance assumption.

## Environmental refresh

The official **MMA/CNUC July 2026 (`CNUC_2026_07`)** geometry is processed through a reproducible GitHub Actions pipeline.

Current municipality screening counts:
- 732 with any CNUC overlap
- 258 intersecting Integral Protection areas
- 347 with >=10% total CNUC overlap
- 213 with >=30% overlap

Updating from August 2025 to July 2026 changed hundreds of lower/middle ranks but caused **zero top-50 membership changes** and **zero Tier-A membership changes** before water was added.

## Four scenarios

| Dimension | Hyperscale AI | Colocation / digital hub | Renewable-first compute | Water-resilient AI* |
|---|---:|---:|---:|---:|
| Energy | 25% | 15% | 35% | 20% |
| Grid | 30% | 25% | 25% | 25% |
| Connectivity | 15% | 30% | 10% | 10% |
| Climate | 10% | 10% | 5% | 15% |
| Environment | 5% | 5% | 10% | 5% |
| Water | 10% | 5% | 10% | 20% |
| Strategic context | 5% | 10% | 5% | 5% |

*The stored scenario key remains `Low-water AI`; the public label is **Water-resilient AI** because the municipality score measures water-risk evidence, while low facility water consumption is a design/compliance gate.*

## Robustness framework

The final shortlist is tested using **1,500 Monte Carlo runs per scenario** with:
- multiplicative lognormal weight perturbation (`sigma = 0.20`);
- water fallback distance-decay sampled between 15 and 60 km;
- deterministic scenario rankings retained for traceability;
- six-dimension Pareto validation independent of strategic/ZPE context.

Tier counts in the water-integrated model:
- **Tier A:** 11
- **Tier B:** 29
- **Tier C:** 69

## Repository structure

```text
src/fetch/        official-source acquisition
src/spatial/      municipal spatial aggregation
src/scoring/      scenario scoring
src/validation/   Monte Carlo / robustness analysis
data/processed/   lightweight reviewer-facing outputs
docs/             methodology, source registry and decision notes
website/          interactive dashboard
.github/workflows reproducible source refresh pipelines
```

## Reproducibility

GitHub Actions independently reproduced the ANA hydrological-access table. The workflow-generated and locally generated water scores match to floating-point precision (maximum observed difference approximately `1.1e-16`).

Current automated refresh workflows:
- **ANA Q95 municipality water evidence**
- **latest CNUC municipality constraints**

## Portfolio / communication assets

- [Portfolio case study](docs/portfolio_case_study.md)
- [Executive decision brief](docs/executive_decision_brief.md)
- [LinkedIn launch draft](docs/linkedin_launch_draft.md)
- [Official-source verification note](docs/source_verification_2026-11-25.md)

## Important limitations

This is a **regional screening system**. A real data-centre investment still requires, at minimum:
- utility load-flow / connection-offer studies;
- firm and additional clean-energy procurement analysis;
- water-right, utility and reclaimed-water feasibility;
- parcel-level environmental, flood, land-title and geotechnical review;
- independent fibre-route and carrier-commercial validation;
- cooling architecture, WUE/PUE and heat-wave engineering;
- construction, tax, logistics, workforce and local-community due diligence.

**A high score means “investigate further,” not “construction-ready.”**