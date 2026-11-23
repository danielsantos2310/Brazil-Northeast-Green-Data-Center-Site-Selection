# Step 03 — ANEEL SIGA first-pass audit

## Source used

Working source: `ANEEL_SIGA_2026-10_MIRROR.csv`, stored in the private Google Drive raw-data workspace.

The source reports a snapshot date of **2026-10-01**. This is a temporary mirror used because the ANEEL open-data host was timing out during acquisition. Before final publication, the pipeline must be rerun against a directly retrieved ANEEL snapshot and the checksum/source date recorded.

## Schema and QA

- National plant records: **25,045**
- Columns: **23**
- Northeast plant records: **3,510**
- Northeast share of SIGA records: **14.01%**
- Northeast states present: **all 9**
- Duplicate `CodCEG` in Northeast subset: **0**
- Blank `CodCEG`: **0**
- Valid Northeast coordinates: **3,332**
- Missing/zero coordinates: **178**
- Coordinate completeness: **94.9%**

Technology codes present in the Northeast subset:

- `EOL` — wind
- `UFV` — solar
- `UHE`, `PCH`, `CGH` — hydro
- `UTE` — thermal

Phases present:

- `Operação`
- `Construção`
- `Construção não iniciada`

## First energy finding

Operating wind + solar capacity, using **fiscalized MW only for plants in Operação**:

| Rank | State | Operating wind + solar MW | Wind MW | Solar MW | Non-operating wind + solar granted MW |
|---:|---|---:|---:|---:|---:|
| 1 | BA | 14,889.2 | 11,832.1 | 3,057.1 | 21,007.4 |
| 2 | RN | 12,839.3 | 10,726.0 | 2,113.2 | 5,831.6 |
| 3 | PI | 6,800.6 | 4,396.3 | 2,404.2 | 13,332.2 |
| 4 | CE | 4,988.2 | 2,690.3 | 2,297.9 | 13,682.2 |
| 5 | PE | 2,770.3 | 1,265.1 | 1,505.2 | 2,506.0 |
| 6 | PB | 1,949.0 | 1,234.2 | 714.7 | 5,013.4 |
| 7 | MA | 430.4 | 426.0 | 4.4 | 356.4 |
| 8 | SE | 35.3 | 34.5 | 0.8 | 782.5 |
| 9 | AL | 4.9 | 0.0 | 4.9 | 102.7 |

### Interpretation

This immediately supports the renewable-resource hypothesis, but it **does not rank data-centre sites yet**.

- Bahia and Rio Grande do Norte lead the current operating wind/solar fleet.
- Ceará and Piauí show large granted non-operating wind/solar pipelines.
- Granted pipeline capacity must not be interpreted as available electricity, spare transmission capacity, or future delivered energy.
- Plant proximity also must not be interpreted as grid connection availability.

## Coordinate quality

Coordinate completeness by technology:

| Technology | Plants | Missing coordinates | Completeness |
|---|---:|---:|---:|
| EOL | 1,380 | 34 | 97.5% |
| UFV | 1,687 | 140 | 91.7% |
| UTE | 385 | 4 | 99.0% |
| CGH | 30 | 0 | 100% |
| UHE | 16 | 0 | 100% |
| PCH | 12 | 0 | 100% |

The missing coordinates mean municipality-level analysis should not rely solely on plant point coordinates.

## Municipality rule

`DscMuninicpios` can contain multiple municipalities for one plant. We will **not duplicate a plant's full MW into every listed municipality**, because that would double-count capacity.

The next GIS stage will use the plant centroid where coordinates exist and spatially join points to official IBGE municipality polygons. Multi-municipality and missing-coordinate cases will be retained for QA and handled separately.

## Data minimization

The raw ANEEL file remains unchanged in private Drive storage. The public cleaned output drops `DscPropriRegimePariticipacao`, because ownership text can contain identifying information and is unnecessary for site-selection scoring.

## Next dependency

The next dataset required is the official **IBGE 2025 municipal mesh**. It will provide:

- municipality polygons
- canonical IBGE municipality codes
- spatial boundaries for all nine Northeast states
- the geographic base for plant-to-municipality spatial joins

No suitability score should be calculated before the municipality geometry and grid layers are integrated.
