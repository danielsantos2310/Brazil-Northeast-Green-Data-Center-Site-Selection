# Step 07 — Solar and wind resource foundation

## Status

**In progress — wind resource complete; INPE/LABREN solar acquisition requires a user acceptance step.**

Step 07 adds climatological renewable-resource quality to the municipality
screen. These variables remain separate from installed ANEEL capacity, ONS
operational evidence and commercial/PPA availability.

## Wind — Global Wind Atlas v4

Official source:

https://globalwindatlas.info/en/download/gis-files

Terms:

https://globalwindatlas.info/en/about/TermsOfUse

The Global Wind Atlas v4 provides 250 m wind-resource mapping at 10, 50, 100,
150 and 200 m. The project uses the following 100 m layers:

- Mean Wind Speed
- Mean Power Density

Mean power density is retained because GWA describes it as a more accurate
indication of available wind resource than mean wind speed alone.

### License and attribution

The GWA Works are licensed under CC BY 4.0 unless another licence is expressly
stated. Publication must include the DTU/World Bank/ESMAP attribution requested
by GWA and cite the peer-reviewed Global Wind Atlas reference.

### Acquisition design

The official Brazil country exports are large:

- mean wind speed 100 m: **515,162,560 bytes**
- mean power density 100 m: **546,272,727 bytes**

Both official endpoints support HTTP byte-range requests.

The repository therefore uses:

```text
src/fetch/download_gwa_northeast.py
```

to read only the exact Step 04 IBGE Northeast extent plus a 0.10° total buffer.
No resampling is performed. The extracted Northeast rasters preserve the
original 0.0025° grid (~250 m) and original pixel values.

The national source URLs, national byte sizes, raster metadata, extracted
window, subset byte sizes and SHA-256 checksums are recorded in:

```text
gwa4_northeast_manifest.json
```

Because the Drive connector has a 100 MB transfer limit, the verified
Northeast source window is additionally split into lossless per-state raster
windows using the official Step 04 IBGE 2025 state extents. The per-state files
are storage/transfer subsets only; analytical zonal statistics are produced
from the continuous Northeast raster.

### Wind municipality metrics

The output retains all **1,794** Northeast municipalities.

For both 100 m mean wind speed and 100 m mean power density, the municipality
table contains:

- valid source-pixel count;
- municipality mean;
- median;
- 90th percentile;
- maximum.

No raster resampling is applied before zonal statistics.

Initial QA shows complete coverage of all 1,794 municipalities for both
resource layers.

Examples of strongest municipality-average wind resource in the first pass:

| Municipality | State | Mean wind speed 100 m (m/s) | Mean power density 100 m (W/m²) |
|---|---|---:|---:|
| Bodó | RN | 10.41 | 880 |
| Marcolândia | PI | 9.53 | 781 |
| São José do Sabugi | PB | 9.09 | 667 |
| Santa Luzia | PB | 8.93 | 653 |
| Cacimba de Areia | PB | 8.76 | 619 |

These values describe climatological resource quality only. They are not a
site ranking and do not imply available generation, grid capacity or a PPA.

## Solar — INPE/LABREN Brazilian Atlas of Solar Energy

Official metadata:

https://labren.ccst.inpe.br/projetos/atlas_2017/atlas_solar_2017_metadados.pdf

The 2017 second-edition database contains annual and monthly average daily
irradiation for:

- Global Horizontal Irradiation (GHI)
- Diffuse irradiation
- Direct Normal Irradiation (DNI)
- Tilted-plane irradiation
- PAR

The source uses SIRGAS 2000 and a 0.1° x 0.1° grid (approximately 10 km), based
on the BRASIL-SR model and satellite inputs from 1999–2015.

For this project, the initial solar screening variable will be annual GHI,
with monthly values retained for seasonality checks.

### Current acquisition boundary

The LABREN download interface requires the user to make an explicit acceptance
declaration before specific database downloads are released. The project will
not automate or bypass that legal acknowledgement.

The metadata also states that the database may not be reproduced/copied in
whole or part for commercial purposes without express CCST/INPE permission,
and requires attribution to LABREN/CCST/INPE.

Therefore:

- the source and methodology are verified;
- no LABREN data file is claimed as acquired yet;
- Step 07 remains **in progress** until the user performs the acceptance/download
  or an explicitly approved alternative solar source is selected.

## Gate for Step 08

Step 07 can be marked complete only after:

- GWA wind municipality metrics are validated and archived;
- the solar source is legitimately acquired;
- solar municipality metrics are generated for the same 1,794-municipality
  universe;
- source/licence attribution is recorded;
- solar/wind resource potential remains separate from actual generation,
  grid access and contractual energy availability.
