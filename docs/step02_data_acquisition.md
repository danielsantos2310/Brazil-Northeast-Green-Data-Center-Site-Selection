# Step 02 — Data acquisition

## Goal

Freeze the first reproducible raw-data snapshot before analysis begins.

## Programmatic downloads

Run:

```bash
python src/fetch/download_core.py
```

The script downloads:

1. `aneel_siga_empreendimentos_geracao.csv`
2. `ons_subestacoes_operacao.csv`
3. `epe_subestacoes_existentes.geojson`
4. `epe_subestacoes_planejadas.geojson`

It also creates:

```text
data/raw/download_manifest.json
```

with source URL, byte size and SHA-256 checksum.

## Manual / licence-gated downloads

These should not be automated until their exact terms and current download flow are respected.

### INPE LABREN Solar Atlas

Official source:
https://labren.ccst.inpe.br/atlas_2017.html

Target local name:

```text
data/raw/inpe_solar_global_horizontal.zip
```

Use the full CSV or GIS resource for Global Horizontal Irradiation and preserve the original archive.

### Global Wind Atlas

Official source:
https://globalwindatlas.info/en/download/gis-files

Target local name:

```text
data/raw/global_wind_atlas_brazil_100m.tif
```

Select Brazil and download the 100 m wind-resource GeoTIFF. Record Global Wind Atlas v4 attribution.

### INMET weather

Official source:
https://portal.inmet.gov.br/dadoshistoricos/

Initial target files:

```text
data/raw/inmet_2020.zip
data/raw/inmet_2021.zip
data/raw/inmet_2022.zip
data/raw/inmet_2023.zip
data/raw/inmet_2024.zip
data/raw/inmet_2025.zip
data/raw/inmet_2026.zip
```

We will use several years rather than a single year for climate metrics.

### IBGE 2025 municipal mesh

Official source:
https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/

Target local name:

```text
data/raw/ibge_municipios_2025.zip
```

We will only rename after verifying the exact downloaded archive. The original filename should also be recorded in the provenance log.

## QA gate before Step 03

Do not start scoring yet.

Step 02 is complete only when:

- every raw file opens successfully
- source URLs are recorded
- hashes are recorded
- CRS is identified for all geospatial layers
- municipality/state coverage is checked
- planned and operating infrastructure are kept separate
- raw files remain unmodified
