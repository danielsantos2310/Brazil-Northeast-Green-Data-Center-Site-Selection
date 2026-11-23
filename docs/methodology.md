# Methodology

## Project type

This repository implements a **public-data screening model** for data-centre site selection in Northeast Brazil.

It is not an engineering connection study, a land-acquisition study or an investment-grade feasibility opinion.

## Geographic unit

The first analytical unit is the municipality across all nine Northeast states:

- Maranhão (MA)
- Piauí (PI)
- Ceará (CE)
- Rio Grande do Norte (RN)
- Paraíba (PB)
- Pernambuco (PE)
- Alagoas (AL)
- Sergipe (SE)
- Bahia (BA)

## Planned dimensions and default weights

| Dimension | Weight |
|---|---:|
| Energy resource & generation ecosystem | 25% |
| Grid infrastructure | 25% |
| Digital connectivity | 15% |
| Climate & cooling | 10% |
| Water | 10% |
| Land & environment | 10% |
| Economy & incentives | 5% |

Scores will be normalized to 0–100 as **relative screening scores**, not probabilities.

## Hard exclusions before scoring

Where reliable spatial evidence exists, candidate areas should be excluded or strongly constrained for:

- protected areas and legally constrained conservation zones
- severe environmental restrictions
- unacceptable flood/water risk
- other legally protected or socially sensitive territories added in later phases

## Key safeguards

- Substation proximity is **not** spare grid capacity.
- Installed renewable MW is **not** actual generation.
- Wind/solar resource is **not** PPA availability.
- Curtailment is **not** automatically usable cheap energy.
- Fibre presence is **not** route diversity, dark-fibre capacity or guaranteed latency.
- Missing data must never silently become zero.
- Municipal screening does not replace parcel-level due diligence.

## Scenario profiles

Later versions will support:

- Hyperscale AI
- Colocation / edge
- Renewable-first
- Low-water AI

Each scenario changes weights while keeping raw indicators and methodology visible.
