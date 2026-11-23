# Step 05 — EPE grid-infrastructure foundation

## Verified source

EPE's official Webmap exposes Brazilian energy-system layers through ArcGIS services and supports vector/raster download plus WMS access.

Main source:

https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/webmap-epe

ArcGIS service:

https://gisepeprd2.epe.gov.br/arcgis/rest/services/SMA/WFS_Webmap_EPE/MapServer

## Layers used

The fetch pipeline resolves these names dynamically:

- Subestações - Base Existente
- Subestações - Expansão Planejada
- Linhas de Transmissão - Base Existente
- Linhas de Transmissão - Expansão Planejada

This avoids relying on hard-coded ArcGIS layer IDs.

The existing-substation layer exposes fields including:

- `Nome`
- `Ano_Opera`
- `Tensao`
- `Concession`
- `longitude`
- `latitude`
- `CD_MUN`

The planned-substation layer includes expected operation year and voltage.

EPE data use SIRGAS 2000 (EPSG:4674).

## Acquisition

```bash
python src/fetch/download_epe_grid.py
```

This downloads national raw GeoJSON layers and writes a SHA-256 manifest.

Original files should also be preserved under the private Drive folder:

```text
01_Raw_Data/EPE/
```

## Intended metrics

Once IBGE municipality geometry is available, first-pass metrics include:

- distance to nearest existing substation
- distance to nearest planned substation
- distance to nearest 230 kV+ infrastructure
- count of high-voltage substations within chosen radii
- distance to transmission corridors
- evidence of planned reinforcement

## Critical methodological rule

**Substation or line proximity is not spare grid capacity.**

A municipality can be physically close to a 500 kV or 230 kV asset and still be unsuitable for a hyperscale load due to:

- thermal limits
- stability constraints
- transformer limits
- fault-level constraints
- network topology
- queue/connection commitments
- reinforcement lead times

Therefore grid proximity will be treated as a **screening indicator**, while connection capacity will receive a separate evidence/confidence field based on EPE/ONS planning studies.

## Next grid work

After the raw EPE layers are downloaded:

1. filter to Northeast Brazil;
2. normalize voltage fields;
3. calculate municipality-level proximity;
4. add ONS operating-grid and curtailment evidence;
5. identify locations where planned large electro-intensive loads are already being studied.
