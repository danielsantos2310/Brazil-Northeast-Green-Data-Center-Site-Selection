# Step 06 — ONS operational-grid and curtailment evidence

## Status

**Complete — 2026-11-23.**

Step 06 uses the current ONS operating-substation snapshot plus the completed
October 2026 constrained-off datasets for wind and solar. October is used for
the first operational pass because it aligns with the October 2026 ANEEL
working snapshot and avoids mixing a partial November month into the analysis.

## Verified sources

### Operating substations

https://dados.ons.org.br/dataset/subestacao

ONS publishes substations in operation in the Rede de Operação (Rede Básica +
Rede Complementar) with base voltage >=69 kV. The source is updated daily and
does not provide historical snapshots.

### Wind constrained-off

https://dados.ons.org.br/dataset/restricao_coff_eolica_usi

### Solar constrained-off

https://dados.ons.org.br/dataset/restricao_coff_fotovoltaica

The curtailment datasets contain 30-minute records and are subject to recurrent
consistency updates by ONS.

ONS data are released under Creative Commons Attribution terms.

## Reproducible acquisition

The repository downloader resolves current resources through the ONS CKAN API
rather than hard-coding monthly resource URLs:

```bash
python src/fetch/download_ons_core.py --months 2026-10
```

The GitHub Actions acquisition workflow is:

```text
.github/workflows/fetch-ons-core.yml
```

The workflow verifies file size and SHA-256 before publishing a short-lived
artifact for transfer to the private Drive raw-data workspace.

Original files are preserved under:

```text
Google Drive/
Brazil-Northeast-Green-Data-Center-Site-Selection/
01_Raw_Data/
ONS/
```

## Operating-substation QA

The current source contains:

- source rows: **1,691**
- unique `id_subestacao`: **916**
- unique substations with plausible coordinates: **907**
- unique substations carrying a Northeast state code: **308**
- Northeast state-coded substations with valid coordinates: **302**
- those physically inside an IBGE Northeast municipality polygon: **298**

The source has multiple rows per substation because voltage levels/bus records
are represented separately. The pipeline consolidates them to one station and
retains the maximum listed voltage.

ONS station proximity is calculated independently from EPE. It is an
operational-network cross-check, not a replacement for the EPE planning/grid
layer.

## October 2026 constrained-off QA

### Wind

- national rows: **226,128**
- Northeast rows: **205,296**
- Northeast ONS plant/complex IDs: **140**
- Northeast connection points: **59**
- restricted 30-minute asset intervals: **88,246**
- reported restriction asset-minutes: **2,519,876**

### Solar

- national rows: **124,992**
- Northeast rows: **84,816**
- Northeast ONS plant/complex IDs: **57**
- Northeast connection points: **45**
- restricted 30-minute asset intervals: **26,131**
- reported restriction asset-minutes: **735,116**

`restriction_asset_minutes` is summed across generating assets/intervals. It
must not be interpreted as simple wall-clock regional minutes.

## Connection-point geocoding

Curtailment is geographically assigned through ONS `id_pontoconexao`.

For October 2026 Northeast data:

- wind: **55** connection points map directly through an ONS station-code
  prefix and **4** use an exact EPE substation-name fallback;
- solar: **44** map directly and **1** uses the exact-name fallback;
- unresolved Northeast connection points: **0**.

The five exact-name fallbacks are:

- Riachão II
- Chapada I
- Chapada II
- Chapada III
- Simplice

The fallback is exact after deterministic text normalization. No fuzzy
nearest-name matching is used.

After geocoding, all 104 technology/connection-point records fall inside an IBGE
Northeast municipality and their ONS state code agrees with the spatially joined
state.

## Municipality indicators

The output retains all **1,794** Northeast municipalities. Municipalities
without ONS wind/solar records receive zero exposure metrics rather than being
removed from the candidate universe.

Operating-grid fields include:

- nearest ONS operating substation >=69 kV;
- nearest ONS operating substation >=230 kV;
- station identities and maximum voltage;
- counts of >=69 kV stations within 25 km and 50 km;
- counts of >=230 kV stations within 25 km and 50 km.

For wind and solar separately, the constrained-off fields include:

- 30-minute asset interval count;
- restricted asset interval count and share;
- restriction asset-minutes;
- published REL/CNF/ENE minute columns;
- sum of reported `val_geracaonaorealizadaapurada`;
- sum of reported `val_geracaoreferencia`;
- ratio of those two reported quantities;
- ONS plant/complex count;
- connection-point count.

The non-realized/reference ratio is dimensionless and deliberately avoids
assuming an energy-unit conversion from the 30-minute reported values.

## Main outputs

```text
data/processed/ons_operating_substations_unique.csv
data/processed/ons_operating_substations_northeast.gpkg
data/processed/ons_curtailment_connection_points_2026-10.csv
data/processed/ons_curtailment_connection_points_2026-10.gpkg
data/processed/ons_municipality_operational_metrics_2026-10.csv
data/processed/ons_curtailment_state_summary_2026-10.csv
data/processed/ons_operational_qa.csv
```

A diagnostic table also joins ANEEL + IBGE + EPE + ONS municipality indicators.
It is not a final suitability score.

## Critical methodological rule

**Curtailment is not free electricity, and grid proximity is not connection
capacity.**

High constrained-off exposure can indicate renewable generation being limited
by operational or network conditions. It does not prove that a data-centre load
can connect, receive that power, obtain a PPA, or reduce the same constraint.

The model therefore preserves three separate concepts:

1. **physical grid proximity** — primarily EPE plus ONS cross-check;
2. **operational restriction exposure** — ONS constrained-off evidence;
3. **actual connection feasibility** — project-specific engineering,
   operator/utility studies and commercial due diligence.

Only the first two are approximated from public open data.

## Gate for Step 07

The Step 06 gate is satisfied:

- official ONS raw files are archived and checksum-verified;
- the operating-substation snapshot is normalized and geocoded;
- October 2026 wind and solar constrained-off files are processed;
- all Northeast connection points in the selected month are geographically
  resolved;
- the complete municipality candidate universe is retained;
- curtailment remains analytically separate from grid capacity and energy
  availability claims.
