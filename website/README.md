# Northeast Brazil Green Data Centre — website release candidate

Single-page interactive decision-support story generated from the project's provisional v2 analytical outputs.

## Status

This dashboard is a **provisional release candidate**, not a final investment recommendation.

It deliberately exposes the outstanding evidence gates:
- ANA Q95 hydrological evidence is being refreshed through the repository's reproducible GitHub Actions pipeline and is not yet included in the weighted ranking.
- CNUC protected-area geometry is being refreshed to the official July-2026 release through an automated pipeline.
- Grid infrastructure strength does not imply verified utility connection headroom.
- Fibre provider diversity does not prove route-independent dark fibre or SLA availability.
- Municipality screening does not replace parcel-level due diligence.

## Run locally

From the repository root:

```bash
python -m http.server 8080
```

Open `http://localhost:8080/website/`.

The website reads the same lightweight municipality evidence published with the repository.