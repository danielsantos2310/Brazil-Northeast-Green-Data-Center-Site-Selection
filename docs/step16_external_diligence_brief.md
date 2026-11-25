# Step 16 — External Diligence Brief

**Date:** 25 November 2026  
**Status:** public-data deep dive complete enough to define the first external-diligence queue

## Decision

The v4 municipality model produced 11 Tier-A robust candidates. Step 16 adds a second decision layer without changing that analytical result.

The first five municipalities where the current public evidence justifies the next round of paid/commercial/engineering diligence are:

1. **Bom Jesus da Lapa, BA — external diligence now**
2. **Brumado, BA — external diligence now**
3. **Juazeiro, BA — advance conditionally**
4. **São Gonçalo do Amarante / Pecém, CE — strategic conditional**
5. **Urandi, BA — advance conditionally**

**Parnaíba, PI remains the first reserve challenger.**

This is not an investment ranking and does not mean the other Tier-A municipalities are rejected. It is an allocation of the next diligence effort.

## What Step 16 added

### AdaptaBrasil MCTI baseline climate-risk evidence

The official AdaptaBrasil API is queried reproducibly from GitHub Actions.

- Water-stress indicator ID `2`, baseline year `2020`.
- Flood / flash-flood / urban-flood indicator ID `60041`, baseline year `2015`.

| Municipality | Water-stress risk | Flood risk |
|---|---:|---:|
| Bom Jesus da Lapa | 0.67 — High | 0.47 — Medium |
| Brumado | 0.45 — Medium | 0.75 — High |
| Juazeiro | 0.83 — Very high | 0.76 — High |
| São Gonçalo do Amarante | 0.80 — Very high | 0.28 — Low |
| Urandi | 0.62 — High | 0.46 — Medium |
| Parnaíba | 0.73 — High | 0.70 — High |
| Icó | 0.70 — High | 0.71 — High |
| Paulo Afonso | 0.73 — High | 0.78 — High |
| Caetité | 0.63 — High | 0.62 — High |
| São João do Piauí | 0.59 — Medium | 0.43 — Medium |
| Delmiro Gouveia | 0.75 — High | 0.77 — High |

These indicators are municipality-scale climate-risk screens. They do not replace parcel flood modelling, hydrology, drainage engineering or industrial water studies.

## Current public water-system evidence

### Bom Jesus da Lapa

Federal water-security investment is actively reinforcing the regional system. The second stage of the Adutora da Fé received an order of service in January 2026 with approximately R$230 million in investment. The project expands infrastructure based on São Francisco water.

Interpretation: **positive infrastructure signal**, but the project is primarily public/human water supply. No industrial allocation is assumed.

Official source: https://www.gov.br/mdr/pt-br/noticias/midr-coordena-nova-etapa-da-adutora-da-fe-na-bahia

### Brumado

The second stage of Barragem de Cristalândia progressed through procurement in September 2026 and is intended to raise storage capacity by about 40%.

Interpretation: **positive water-security reinforcement**, but high municipality-scale flood risk remains a parcel-level gate.

Official source: https://www.brumado.ba.gov.br/noticias/715-2026/09/21/licitacao-avanca-e-2-ordf-etapa-da-barragem-de-cristalandia-preve-aumento-de-40-na-capacidade-de-armazenamento

### Juazeiro

The municipal SAAE reported that the system produces about 622 L/s of treated water while about 435 L/s reaches roughly 87,000 registered residences, with approximately 187 L/s lost through the distribution system. The municipality is preparing restructuring and investment.

Interpretation: Juazeiro has very strong raw hydrological evidence, but **network efficiency and climate water stress are material diligence issues**.

Official source: https://www.juazeiro.ba.gov.br/prefeitura-articula-recursos-junto-aos-governos-estadual-e-federal-e-preve-investimentos-proprios-para-reestruturar-o-saae-em-juazeiro/

ANA's 2025 national water-use assessment also identifies substantial demand pressure in Bahia and the São Francisco corridor, including irrigated agriculture around Juazeiro.

Official source: https://conjuntura2025.ana.gov.br/usos-da-agua.html

### São Gonçalo do Amarante / Pecém

The municipality remains the strongest strategic digital-industrial case in the v4 model, with excellent connectivity and ZPE context.

Step 16 does **not** clear its two critical risks: documented EPE near-term grid-access risk and very-high AdaptaBrasil baseline water-stress risk.

Interpretation: advance only if connection timing/headroom and an industrial water strategy can be demonstrated.

### Urandi

The municipality announced water rationing and temporary supply suspension during the 2026 dry season. A new approximately 70 km adductor project is being developed with pumping, storage, distribution and treatment infrastructure.

Interpretation: the strong renewable/grid/climate profile remains interesting, but **current public-supply stress is a real warning** and the reinforcement is not yet an operating industrial supply source.

Official sources:
- https://www.urandi.ba.gov.br/noticias/urandi_inicia_racionamento_e_tera_abastecimento_de_agua_suspenso_neste_domingo-2832
- https://urandi.ba.gov.br/noticias/prefeitura-de-urandi-acompanha-na-embasa-projeto-de-adutora-para-ampliar-abastec-20259/

## Reserve challenger — Parnaíba

Parnaíba has exceptional provider depth, active ZPE context, strong direct Q95 evidence and current public water-system reinforcement.

But it also carries EPE near-term grid-access risk, challenging cooling-climate evidence, high AdaptaBrasil water-stress and flood-risk screens, and 28.5% municipality-level CNUC overlap.

Official water-system sources:
- https://www.pi.gov.br/aguas-do-piaui-amplia-capacidade-de-abastecimento-do-litoral-para-o-b-r-o-bro-e-temporada-de-fim-de-ano/
- https://www.pi.gov.br/bairros-populosos-de-parnaiba-recebem-reforco-no-abastecimento-de-agua/

## Current drought context

Cemaden's October 2026 monitoring reports that severe/extreme drought remained concentrated in parts of the Northeast even as the national total improved. The public Alerta-Secas platform covers all Brazilian municipalities and is useful for current-condition monitoring.

This project treats current drought as **context**, not as a substitute for long-term ANA hydrological evidence or a water-right study.

Official sources:
- https://www.gov.br/cemaden/pt-br/assuntos/monitoramento/impactos-seca/monitoramento-de-seca-para-o-brasil/monitoramento-de-secas-e-impactos-no-brasil-2013-outubro-2026
- https://alertasecas.cemaden.gov.br/

## SINISA status

The official SINISA 2025 results page is verified and publishes 2024-reference-year water-supply and stormwater information/indicator spreadsheets.

In this execution environment, the indicator download portal blocked automated retrieval. No SINISA municipal values have therefore been invented or manually guessed.

Official source: https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/resultados-sinisa/resultados-sinisa-2025

## Five-candidate external diligence plan

### 1 — Bom Jesus da Lapa
1. Formal utility MW/headroom and schedule.
2. Industrial water allocation or alternative supply.
3. Two physically independent fibre paths.
4. Parcel flood, title, environmental and geotechnical screen.

### 2 — Brumado
1. Large-load utility capacity and connection cost.
2. Parcel-specific flood/hydraulic risk.
3. Industrial water source independent of assumptions about future reservoir expansion.
4. Route-diverse fibre.

### 3 — Juazeiro
1. Industrial water allocation under competing São Francisco demand.
2. Utility connection/headroom.
3. Parcel flood and drainage design.
4. Water-system independence/redundancy and fibre-route diversity.

### 4 — São Gonçalo do Amarante / Pecém
1. Resolve the EPE access constraint and obtain an actual connection timeline.
2. Define an industrial/reclaimed-water architecture compatible with very-high climate water stress.
3. Confirm independent carrier routes.
4. Parcel environmental screen.

### 5 — Urandi
1. Demonstrate a reliable industrial water source despite recent public rationing.
2. Verify whether planned reinforcement materially changes long-term supply.
3. Utility capacity.
4. Fibre-route diversity and construction/logistics feasibility.

## Hard stop

No municipality should be promoted from this five-candidate queue to a parcel recommendation until at least these four external gates are evidenced:

- formal utility connection/headroom;
- permitted water supply / water rights;
- independent physical fibre routes;
- viable parcel.

**Public-data evidence can justify where to investigate next; it cannot certify where to build.**
