# Water Integration Method — v4

## Purpose

Add a defensible hydrological-risk dimension without pretending public hydrology is equivalent to industrial water supply.

## Source

ANA/SNIRH `Disponibilidade Hídrica Superficial` FeatureServer. The geometry includes `DISPQ95` in m³/s.

## Direct municipality evidence

For municipalities intersecting mapped ANA reaches, the direct evidence index combines:
- percentile of length-weighted mean Q95; and
- percentile of maximum Q95.

The upstream processing gives each component 50% weight.

## Fallback for municipalities without an intersecting Q95 reach

Municipal boundaries are administrative rather than hydrological. A municipality with no intersecting mapped reach is therefore not assigned zero water.

The nearest mapped ANA reach is identified from the municipality polygon. Its Q95 is converted to a percentile against all retrieved ANA reaches and discounted by distance:

`fallback_water_score = nearest_q95_percentile / (1 + distance_km / decay_km)`

Base `decay_km = 25`.

Evidence confidence is labelled by direct intersection / nearest distance. Supply verification remains false for every municipality.

## Method uncertainty

The joint sensitivity analysis does not trust the 25 km parameter as truth. For each Monte Carlo iteration, the fallback decay scale is sampled log-uniformly from **15–60 km** while scenario weights are also perturbed.

Tier A is not dependent on the fallback rule: all 11 final Tier-A candidates have direct local Q95 intersections.

## What the water score is not

It is not:
- an abstraction right;
- a municipal utility commitment;
- permitted sustainable industrial supply;
- drought-resilience guarantee;
- reclaimed-water availability;
- a cooling-system WUE calculation.

These remain project-level due-diligence gates.

## Reproducibility

`src/fetch/download_ana_water_layers.py` downloads the official geometry with robust paginated retry/backoff.
`src/spatial/process_ana_water_municipalities.py` aggregates direct Q95 evidence.
`src/spatial/build_ana_water_screening_score.py` constructs direct/nearest hydrological-access evidence.
`.github/workflows/fetch-ana-water.yml` reruns the pipeline on GitHub infrastructure.

An independent workflow rerun matched the locally generated water score to machine precision.