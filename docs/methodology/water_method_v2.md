# Water method v2 — Northeast Brazil data-centre screening

## Decision principle
Water is not a single proximity variable. The final project must distinguish:
1. **hydrological surface-water availability**;
2. **current demand pressure / basin stress**;
3. **permitted or contracted industrial supply**;
4. **reclaimed-water availability**;
5. **facility cooling-water efficiency (WUE)**.

Only (1) can currently be computed directly from the downloaded/open ANA layer at municipality scale. Items (3)–(5) are project/parcel due diligence; they must never be inferred from a municipality score.

## Primary spatial evidence — ANA Q95
Official feature layer:
https://portal1.snirh.gov.br/server/rest/services/dados_abertos/Disponibilidade_Hidrica_Superficial/FeatureServer/0

Field `DISPQ95` is surface-water availability in m³/s. ANA describes regulated reaches using reservoir restriction flow plus incremental Q95 (or regulated flow with 100% guarantee when restriction flow is unavailable); unregulated rivers use Q95.

The prepared scripts download Northeast-only polylines and aggregate to IBGE municipalities using exact line/polygon intersection. Outputs include reach count/length, length-weighted Q95, median, p90, maximum, and reach length above 1/10/100 m³/s thresholds.

**These metrics are hydrological evidence only. They are not a water right, permit, utility commitment, sustainable withdrawal guarantee, or data-centre cooling supply.**

## Current demand-pressure context — ANA Conjuntura 2025
https://conjuntura2025.ana.gov.br/balanco-hidrico.html

ANA's current balance uses 2024 demand estimates and classifies water-resource commitment as low (<5%), moderate (5–30%), high (30–70%), very high (70–100%), critical (>100%), or intermittent (zero offer).

Important for this project: ANA explicitly warns that reach-level balance is less representative in the Semi-Arid, where reservoirs, adductors and canals supply water that is not fully represented by the hydrographic network. It cites high shares of demand assigned to intermittent reaches in Piancó-Piranhas-Açu, Ceará coastal basins and Rio Grande do Norte coastal basins.

Therefore the current project will **not** use the older 2013/2014-demand ArcGIS balance as if it were a current municipal water-stress score. Q95 will remain an evidence layer until a structured current-demand-pressure dataset can be joined consistently.

## REDATA gate
Brazil's REDATA regime requires cooling WUE <= 0.05 L/kWh for participating data-centre projects. This is a project-design gate, not a municipal hydrology score. A municipality with abundant water can still fail a REDATA-oriented design, and a low-water closed-loop/liquid-cooled design may succeed in a water-constrained municipality if all legal and engineering requirements are satisfied.

Source: https://www.gov.br/fazenda/pt-br/assuntos/noticias/2026/setembro/regime-especial-de-tributacao-para-servicos-de-datacenter-e-sancionado

## Final integration rule
Until current hydrological pressure and project water strategy are verified:
- `water_score = NOT_SCORED`;
- no neutral fill value;
- scenario weights are renormalized over defensible dimensions;
- the scenario called `low_water_ai` is explicitly labelled a **proxy**, not a final low-water ranking.
