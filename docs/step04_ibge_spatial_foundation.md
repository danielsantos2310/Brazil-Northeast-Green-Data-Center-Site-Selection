# Step 04 — IBGE spatial foundation

## Status

**Complete — 2026-11-23.**

The official **IBGE 2025 Digital Municipal Mesh** for the nine Northeast
states has been acquired, checksum-verified, preserved unchanged in the
private Google Drive raw-data workspace, and spatially joined to the October
2026 ANEEL SIGA working snapshot.

Official sources:

- https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html
- https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/UFs/

## Acquired geography

Only the nine Northeast state archives are used:

- AL
- BA
- CE
- MA
- PB
- PE
- PI
- RN
- SE

The original ZIP archives and `ibge_2025_manifest.json` are retained in:

```text
Google Drive/
Brazil-Northeast-Green-Data-Center-Site-Selection/
01_Raw_Data/
IBGE/
```

The download workflow verifies all nine archives and the manifest before they
are promoted into the working dataset.

## Verified characteristics

- Format: Shapefile
- CRS: **EPSG:4674 / SIRGAS 2000**
- Northeast municipality polygons: **1,794**
- Canonical municipality key: `CD_MUN`, renamed to `ibge_code`
- Municipality name: `NM_MUN`
- State field: `SIGLA_UF`

All 1,794 municipality polygons are retained as the candidate universe,
including municipalities with no ANEEL generation records.

## Reproducible acquisition

Local:

```bash
python src/fetch/download_ibge_2025.py --extract
```

A GitHub Actions acquisition workflow is also available at:

```text
.github/workflows/fetch-ibge-2025.yml
```

It uses the same repository downloader, verifies that all nine state archives
are present, checks recorded byte sizes and SHA-256 hashes, and publishes a
short-lived workflow artifact for controlled transfer to the private Drive
workspace. Raw source archives remain excluded from Git.

## Spatial join

After the cleaned ANEEL Parquet exists:

```bash
python src/spatial/join_aneel_to_ibge.py
```

The Step 04 pipeline:

1. loads all nine IBGE municipality layers;
2. validates polygon geometry and municipality-code uniqueness;
3. normalizes geometry to EPSG:4674;
4. writes the canonical municipality layer used by Step 05;
5. converts valid ANEEL coordinates to point geometry;
6. performs a point-in-polygon municipality join;
7. classifies state-consistent and cross-state assignments;
8. retains the complete 1,794-municipality universe;
9. generates municipality-level operating and pipeline wind/solar metrics;
10. writes QA evidence for unmatched or suspect assignments.

## Execution QA — 2026-11-23

From the October 2026 ANEEL working snapshot:

- Northeast ANEEL records: **3,510**
- ANEEL records passing the broad coordinate screen: **3,332**
- Points inside an IBGE Northeast municipality polygon: **3,323**
- State-consistent polygon assignments: **3,305**
- Cross-state assignments explicitly supported by ANEEL municipality text: **4**
- Accepted municipality assignments used in aggregates: **3,309**
- Unsupported cross-state matches excluded from aggregates: **14**
- Points outside every Northeast municipality polygon: **9**
- Municipality summary rows: **1,794**
- Municipalities with zero operating wind/solar capacity: **1,584**

### Cross-state acceptance rule

A cross-state point/polygon match is only accepted when the joined IBGE
municipality is explicitly named in ANEEL `DscMuninicpios`. Unsupported
cross-state matches remain in QA outputs but do not affect municipality-level
energy metrics.

Points outside all municipality polygons are not silently snapped to the
nearest municipality.

## Main outputs

```text
data/processed/ibge_northeast_municipalities.parquet
data/processed/aneel_ibge_plant_join.parquet
data/processed/aneel_ibge_municipality_energy_summary.csv
data/processed/ibge_spatial_join_qa.csv
data/processed/aneel_ibge_assignment_issues.csv
```

## Important limitations

- Plants without reliable coordinates cannot be assigned by point-in-polygon.
- A plant coordinate represents a reference point, not its full physical footprint.
- Coastal, reservoir and administrative-boundary points can fall just outside polygons.
- Municipality attribution is for screening, not legal siting or land-title analysis.
- Installed/granted generation capacity is not evidence of grid connection headroom.
- Grid proximity and operating constraints are added separately in Steps 05 and 06.

## Gate for Step 05

The Step 04 gate is satisfied:

- official municipal geometry is present and validated;
- the full municipality universe is retained;
- point assignments have explicit QA rules;
- suspect assignments are excluded rather than silently corrected;
- the canonical municipality layer is now produced for EPE grid-proximity processing.
