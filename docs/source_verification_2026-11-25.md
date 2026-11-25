# Official-source verification — 25 November 2026

This note records a fresh verification of the two external source layers most material to the final v4 municipality screening.

## ANA/SNIRH — surface-water availability

Official service checked:
https://portal1.snirh.gov.br/server/rest/services/dados_abertos/Disponibilidade_Hidrica_Superficial/FeatureServer/0

Verified characteristics:
- provider: ANA / SNIRH;
- geometry type: polyline;
- spatial reference: SIRGAS 2000 / EPSG:4674;
- principal screening field: `DISPQ95` (surface-water availability, m³/s);
- service supports JSON / GeoJSON / PBF queries and pagination;
- ANA's service description states that unregulated rivers use Q95 low-flow availability, while regulated reaches incorporate reservoir restriction/regulated-flow logic.

Interpretation retained in the project:
**Q95 is hydrological screening evidence only. It is not a water right, a utility-supply commitment, or proof of a permitted sustainable withdrawal for a data centre.**

## MMA/CNUC — protected areas

Official dataset checked:
https://dados.mma.gov.br/dataset/unidadesdeconservacao

Current release verified:
- `CNUC_2026_07`;
- data updated through July 2026;
- portal last updated 21 August 2026;
- official resources include both CSV inventory and ZIP + SHP geometry.

Canonical project output:
`data/processed/step10_cnuc_municipality_constraints_2026-07.csv`

Interpretation retained in the project:
municipality-level CNUC overlap is a regional screening constraint and does not replace parcel-level environmental licensing, land-title review, or other statutory constraints.

## Release status

The current repository release remains:
**v4 water-integrated municipality screening — 25 November 2026**

Canonical status:
- 1,794 Northeast municipalities;
- water-integrated screening complete;
- July-2026 CNUC environment layer complete;
- 1,500 joint uncertainty runs per scenario;
- 11 Tier-A robust candidates;
- all Tier-A candidates have direct local ANA Q95 evidence;
- all Tier-A candidates are Pareto non-dominated across six core dimensions.

No scoring assumptions were changed by this verification note.
