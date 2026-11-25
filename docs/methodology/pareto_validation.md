# Weight-independent Pareto validation — v2

## Purpose

The scenario rankings use explicit weights. To test whether the robust shortlist is merely an artefact of those weights, this validation removes both the weights and the strategic/ZPE dimension and performs an exact Pareto-dominance test across five core municipality dimensions:

- energy;
- grid infrastructure strength;
- connectivity;
- climate/cooling suitability; and
- environment score.

Water is excluded because it is not yet scored.

A municipality is Pareto non-dominated when no other municipality is at least as strong in all five dimensions and strictly stronger in at least one.

## Result

- Municipalities screened: **1,794**
- Exact non-dominated frontier: **97 municipalities**
- Current Tier-A robust candidates: **17**
- Tier-A candidates on the exact Pareto frontier: **16/17 (94.1%)**

This is a strong independent validation of the Tier-A shortlist because strategic context and all scenario weights are absent from this test.

The sole Tier-A exception is **Igaporã, Bahia**. It is dominated by **Caetité, Bahia** across all five core dimensions in the current v2 feature table. That does not make Igaporã infeasible; it means the current public-data screen contains no core-dimension reason to prefer it over Caetité before parcel-level considerations are introduced.

## Interpretation

This test should remain separate from the MCDA score:

- MCDA answers: *which municipalities best fit a stated strategy?*
- Monte Carlo answers: *how stable is that result to plausible weighting changes?*
- Pareto analysis answers: *which municipalities cannot be improved in one core dimension without sacrificing at least one other core dimension?*
- Due-diligence gates answer: *can a real project actually proceed?*

Together, these layers reduce dependence on any single scoring assumption.

## Limitation

The exact frontier contains 97 municipalities because five objectives create many legitimate trade-offs. It is therefore a **validation layer, not a shortlist by itself**. Final conclusions still require the pending water layer, July-2026 CNUC refresh and project/parcel due diligence.
