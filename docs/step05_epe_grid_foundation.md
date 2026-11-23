# Step 05 — EPE grid-infrastructure foundation

## Status

**Complete — 2026-11-23.**

EPE's official Webmap grid layers have been acquired, geometry-validated,
checksum-verified, preserved in the private Drive raw-data workspace, and
converted into municipality-level screening indicators for all 1,794 Northeast
municipalities.

## Verified source

Main source:

https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/webmap-epe

Geometry-bearing ArcGIS REST service used by the pipeline:

https://gisepeprd2.epe.gov.br/arcgis/rest/services/SMA/WMS_Webmap_EPE/MapServer

### Important service correction

During execution, the parallel
`SMA/WFS_Webmap_EPE/MapServer` returned the expected feature attributes but
**null geometry**. The downloader was therefore corrected to use the official
`SMA/WMS_Webmap_EPE/MapServer` REST service, which returns the full point and
line geometry.

The fetcher now refuses to save any EPE layer containing null geometry, so this
failure mode cannot silently pass validation again.

## Layers used

Layer names are still resolved dynamically. On 2026-11-23 they resolved to:

- Subestações - Expansão Planejada — layer 9
- Linhas de Transmissão - Expansão Planejada — layer 10
- Subestações - Base Existente — layer 20
- Linhas de Transmissão - Base Existente — layer 21

The repository does not depend on those numeric IDs; they are recorded here for
provenance only.

## Raw acquisition QA

Verified national feature counts:

- existing substations: **928**
- planned substations: **179**
- existing transmission lines: **2,244**
- planned transmission lines: **439**

Every promoted raw feature has non-null geometry and all five raw files
(including the manifest) match their recorded SHA-256 checksums.

Original files are preserved under:

```text
Google Drive/
Brazil-Northeast-Green-Data-Center-Site-Selection/
01_Raw_Data/
EPE/
```

## Northeast infrastructure

After spatial filtering against the Step 04 IBGE municipality universe:

- existing substations inside Northeast municipalities: **353**
- planned substations inside Northeast municipalities: **82**
- existing transmission lines intersecting at least one Northeast municipality: **717**
- planned transmission lines intersecting at least one Northeast municipality: **185**

For these four EPE layers, Northeast infrastructure is 230 kV or above after
voltage normalization. Substation values such as `525/230` are parsed using
the maximum listed voltage rather than only the first text fragment.

## Municipality metrics

The output retains all **1,794** IBGE Northeast municipalities.

Distances are measured from a municipality representative point to the nearest
national EPE high-voltage asset. National targets are intentionally retained:
an asset immediately outside the formal Northeast boundary can still be the
closest physical grid infrastructure to a border municipality.

The region-wide screening projection is a SIRGAS-compatible Lambert Conformal
Conic centered on Northeast Brazil. A one-municipality-per-state validation
against geodesic nearest-substation distances produced a maximum absolute
relative error of approximately **0.54%**.

Current metrics include:

- nearest existing >=230 kV substation distance and identity
- nearest planned >=230 kV substation distance and identity
- nearest existing >=230 kV transmission-line distance and identity
- nearest planned >=230 kV transmission-line distance and identity
- existing >=230 kV substations within 25 km and 50 km
- planned >=230 kV substations within 25 km and 50 km
- existing >=230 kV line intersects municipality
- planned >=230 kV line intersects municipality

Current screening coverage:

- municipalities with an existing substation within 25 km: **521**
- municipalities with an existing substation within 50 km: **1,220**
- municipalities intersected by an existing 230 kV+ line: **907**

## Main outputs

```text
data/processed/epe_northeast_substations_existing.gpkg
data/processed/epe_northeast_substations_planned.gpkg
data/processed/epe_northeast_lines_existing.gpkg
data/processed/epe_northeast_lines_planned.gpkg
data/processed/epe_municipality_grid_proximity.csv
data/processed/epe_grid_qa.csv
```

A separate diagnostic table joins Step 03/04 energy metrics to the Step 05 grid
metrics. It is **not** a final suitability score.

## Critical methodological rule

**Substation or line proximity is not spare grid capacity.**

A municipality can be close to 230/500/800 kV infrastructure and still be
unsuitable for a hyperscale load because of transformer headroom, thermal or
stability constraints, fault levels, topology, committed connection queues,
reinforcement lead times or commercial connection conditions.

Step 05 therefore contributes physical grid-access indicators only. Step 06
adds ONS operating-grid and curtailment evidence. Later due diligence must still
confirm actual connection feasibility with the relevant operator/utility.

## Gate for Step 06

The Step 05 gate is satisfied:

- EPE raw layers are preserved and checksum-verified;
- geometry is present and explicitly validated;
- the complete 1,794-municipality universe is retained;
- both substation and transmission-line proximity are available;
- planned reinforcement is separated from existing infrastructure;
- proximity is explicitly separated from connection-capacity claims.
