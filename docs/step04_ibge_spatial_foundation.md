# Step 04 — IBGE spatial foundation

## Why this dataset comes next

ANEEL SIGA contains both coordinates and a free-text municipality field. Some plants list more than one municipality, so assigning a plant's full capacity to every listed municipality would double-count generation capacity.

The official **IBGE 2025 Digital Municipal Mesh** provides the canonical municipality polygons and geocodes needed for point-in-polygon spatial joins.

Official sources:

- https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html
- https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/UFs/

## Verified characteristics

The 2025 mesh is distributed as Shapefile, uses **SIRGAS 2000**, a geographic coordinate system, and UTF-8 text encoding. The 2025 publication contains 5,573 geocodes nationally (including municipalities and special territorial units).

For this project we only download:

- AL
- BA
- CE
- MA
- PB
- PE
- PI
- RN
- SE

This avoids downloading the much larger Brazil-wide archive.

## Reproducible download

```bash
python src/fetch/download_ibge_2025.py --extract
```

The script creates a SHA-256 manifest for provenance.

The original ZIP files should also be copied to:

```text
Google Drive/
Brazil-Northeast-Green-Data-Center-Site-Selection/
01_Raw_Data/
IBGE/
```

## Spatial join

After the cleaned ANEEL Parquet exists:

```bash
python src/spatial/join_aneel_to_ibge.py
```

The join:

1. loads all nine IBGE municipality layers;
2. normalizes them to EPSG:4674 (SIRGAS 2000);
3. converts valid ANEEL coordinates to points;
4. reprojects those points to SIRGAS 2000;
5. performs a point-in-polygon municipality join;
6. generates municipality-level operating and pipeline wind/solar metrics.

## Important limitations

- Plants without coordinates cannot be assigned through point-in-polygon.
- A plant centroid represents the plant location, not its full physical footprint.
- Plants exactly on administrative boundaries require QA.
- Municipality attribution is used for screening, not legal siting or land-title analysis.
- Capacity around a municipality does not prove grid connection availability.

## Gate for the next stage

Do not calculate a data-centre suitability score until:

- the municipality join is validated;
- unmatched points are reviewed;
- transmission/substation data are added;
- renewable resource potential is kept separate from installed generation capacity.
