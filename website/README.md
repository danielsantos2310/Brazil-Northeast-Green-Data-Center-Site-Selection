# Website — water-integrated v4

This folder contains the interactive release-candidate dashboard for the Northeast Brazil Green Data Centre Site Selection project.

## Analytical baseline

- 1,794 Northeast municipalities
- ANA/SNIRH Q95 hydrology integrated
- MMA/CNUC July 2026 integrated
- exact-coordinate INMET climate layer
- four scenario rankings
- 1,500-run joint scenario-weight + water-method sensitivity
- 11 Tier-A robust candidates
- all 11 Tier-A candidates are Pareto non-dominated across energy, grid, connectivity, climate, environment and water

## Interpretation

The water dimension is **hydrological-access screening evidence**, not permitted or contracted supply.

A final data-centre project still requires:
- utility grid connection/headroom studies;
- water-right / utility / reclaimed-water feasibility;
- parcel-level environmental and legal review;
- carrier route-diversity and SLA validation;
- cooling design and facility WUE compliance;
- geotechnical, logistics, tax and construction due diligence.

## Run locally

From the repository root:

```bash
python -m http.server 8080
```

Open `http://localhost:8080/website/`.
