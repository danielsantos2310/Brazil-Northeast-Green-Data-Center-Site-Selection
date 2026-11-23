# Step 06 — ONS operational-grid and curtailment evidence

## Verified sources

### Substations

ONS publishes **Subestação da Rede de Operação**, containing operating substations in the Rede de Operação (Rede Básica + Rede Complementar) with base voltage **>= 69 kV**.

Source:

https://dados.ons.org.br/dataset/subestacao

ONS states that this dataset is refreshed daily and does not provide historical snapshots.

### Wind constrained-off

https://dados.ons.org.br/dataset/restricao_coff_eolica_usi

### Solar constrained-off

https://dados.ons.org.br/dataset/restricao_coff_fotovoltaica

ONS also publishes much larger plant-detail datasets. Those are deliberately not part of the first acquisition batch because monthly files can be very large. We will only use detail data if the aggregate files cannot support the shortlist analysis.

ONS data are released under Creative Commons Attribution terms.

## Why curtailment matters

Curtailment/restriction data help identify where renewable output is being limited by operational or network conditions.

However:

> **Curtailment is not free electricity.**

A high-curtailment area can be analytically interesting for flexible loads, but a data centre cannot assume curtailed energy is contractually available, firm, dispatchable, or capable of being delivered to its connection point.

## Acquisition strategy

The downloader resolves current resources through the ONS CKAN API.

Download the current substation snapshot only:

```bash
python src/fetch/download_ons_core.py
```

Add specific curtailment months when needed:

```bash
python src/fetch/download_ons_core.py --months 2026-10 2026-11
```

This avoids accidentally downloading gigabytes of historical detail files.

Archive the original resources in:

```text
01_Raw_Data/ONS/
```

## Planned use

ONS will contribute separate evidence for:

- operating-grid infrastructure cross-checks;
- curtailment/restriction exposure;
- renewable operating conditions;
- grid evidence confidence.

It will **not** be merged into a single "grid capacity" variable.

## Data-centre interpretation

The eventual model should distinguish at least three concepts:

1. **Grid proximity** — EPE/ONS infrastructure location.
2. **Grid stress / renewable restrictions** — ONS operational evidence.
3. **Connection feasibility** — planning studies and project-specific operator/utility due diligence.

Only the first two can be approximated well from public open data.
