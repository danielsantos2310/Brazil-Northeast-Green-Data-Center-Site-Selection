# Brazil Northeast Green Data Center Site Selection Analytics

A public-data geospatial screening project to identify high-potential municipalities in Northeast Brazil for renewable-powered data-centre development.

## Objective

Evaluate municipalities across the nine Northeast states using transparent evidence on:

- renewable energy resource and generation
- grid infrastructure
- digital connectivity
- climate and cooling
- water
- land and environmental constraints
- economy, logistics and incentives

The model is a **screening tool**, not an investment-grade site certification. Public data can identify promising municipalities, but it cannot confirm spare grid connection capacity, commercial fibre availability, land title, water allocation or negotiated PPA terms.

## Study area

MA, PI, CE, RN, PB, PE, AL, SE and BA.

## Storage strategy

This project deliberately separates working data from the public repository.

### Google Drive — research workspace

Google Drive is the source-file workspace for:

- original/raw downloads
- large GIS and raster files
- working/interim datasets
- processed analytical files before publication
- notebook exports and QA material
- charts, maps and tables
- publication/portfolio assets

Raw source files are preserved unchanged and organized by agency/provider.

### GitHub — reproducible/public project

GitHub contains:

- Python source code and fetch/ETL scripts
- notebooks suitable for publication
- methodology and source provenance
- tests and validation logic
- lightweight public processed outputs when appropriate
- the final interactive website

Large raw datasets are intentionally excluded from Git. Reproducible download scripts and source references document how to recover them.

### GitHub Pages — final publication layer

When the analysis is validated, the final static site will be built from `website/` and published through GitHub Pages. Only optimized, public, licence-compatible web data and assets will be included.

## Project structure

```text
data/
  raw/
  interim/
  processed/
  reference/
notebooks/
src/
  fetch/
  clean/
  spatial/
  scoring/
  validation/
tests/
outputs/
  maps/
  charts/
  tables/
website/
docs/
```

## Current status

- Step 01 — Project foundation: **complete**
- Step 02 — Initial data acquisition: **in progress**
- Step 03 — ANEEL SIGA first-pass audit and ETL: **complete**
- Step 04 — IBGE municipality spatial foundation: **complete**
- Step 05 — EPE grid-infrastructure foundation: **complete**
- Step 06 — ONS operational-grid/curtailment foundation: **pipeline prepared**
- Step 07 — Solar + wind resource: **pending**
- Step 08 — Fibre/connectivity: **pending**
- Step 09 — Climate + cooling + water: **pending**
- Step 10 — Environment/land constraints: **pending**
- Step 11 — Suitability model: **pending**
- Step 12 — Candidate locations + sensitivity analysis: **pending**
- Step 13 — Full interactive website: **pending**
- Step 14 — GitHub Pages + portfolio + LinkedIn: **pending**

Step 04 uses the official 2025 IBGE municipal meshes for all nine Northeast states. The raw state ZIPs are checksum-verified and preserved in the private Drive workspace; the public repository retains reproducible acquisition and spatial-processing code instead of raw GIS archives.

The October 2026 ANEEL mirror is being used only as a working snapshot while the official ANEEL host is unavailable. Final publication will refresh the source from ANEEL.

## Planned analytical workflow

1. Source audit and provenance
2. Geospatial foundation
3. Energy and grid analysis
4. Connectivity, climate, water and environmental layers
5. Scoring model and scenario profiles
6. Sensitivity analysis and validation
7. Candidate shortlist
8. Interactive website
9. Final documentation and publication

## Initial authoritative sources

- ANEEL SIGA
- EPE Webmap and transmission studies
- ONS Dados Abertos
- IBGE municipal boundaries and socioeconomic statistics
- INPE LABREN Solar Atlas
- Global Wind Atlas
- INMET historical weather
- ANATEL infrastructure data
- ANA/SNIRH
- MMA/ICMBio
- MDIC ZPE

## Methodological principle

A high score means **deserves deeper engineering and commercial due diligence**. It does not mean a site is automatically ready for construction.
