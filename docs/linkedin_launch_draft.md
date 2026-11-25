# LinkedIn launch draft — Northeast Brazil Green Data Centre Site Selection

I’ve completed a data-driven project exploring a question at the intersection of infrastructure, renewable energy, geospatial analysis and data engineering:

**Where in Northeast Brazil does the evidence support deeper investigation for green data-centre development?**

I built a reproducible screening model covering **1,794 municipalities**, combining evidence from IBGE, ANEEL, EPE, ONS, INPE/LABREN, Global Wind Atlas, ANATEL, INMET, ANA/SNIRH, MMA/CNUC and MDIC/ZPE.

The model evaluates seven dimensions: energy, grid, connectivity, climate, environment, water and strategic context.

One rule shaped the project: **do not turn incomplete evidence into fake certainty.**

So transmission proximity is not treated as spare connection capacity, renewable pipeline MW is not treated as firm available supply, provider count is not treated as physical fibre redundancy, ANA Q95 is not treated as a water permit, and municipality ranking is not treated as parcel feasibility.

The final version integrates official ANA hydrological evidence and the July 2026 MMA/CNUC protected-area layer.

That changed the result.

Before water integration, the robust Tier-A set contained 17 municipalities. After water became real evidence, it contracted to **11**.

The final model uses **1,500 Monte Carlo runs per scenario**, water-method uncertainty testing and six-dimension Pareto validation.

Final Tier-A municipalities:

São Gonçalo do Amarante (CE), Juazeiro (BA), Bom Jesus da Lapa (BA), Parnaíba (PI), Urandi (BA), Paulo Afonso (BA), Caetité (BA), São João do Piauí (PI), Brumado (BA), Icó (CE) and Delmiro Gouveia (AL).

All 11 have direct mapped ANA Q95 evidence and are Pareto non-dominated across energy, grid, connectivity, climate, environment and water.

The result is intentionally a **due-diligence funnel**, not an investment recommendation. A real project would still require utility studies, water rights, fibre-route validation, parcel analysis, permitting, cooling engineering and project economics.

The repository includes the processing pipeline, scoring methodology, sensitivity analysis, automated GitHub Actions workflows and an interactive dashboard.

Repository:
https://github.com/danielsantos2310/Brazil-Northeast-Green-Data-Center-Site-Selection

Interactive dashboard:
https://danielsantos2310.github.io/Brazil-Northeast-Green-Data-Center-Site-Selection/

#DataAnalytics #Python #Geospatial #DataEngineering #RenewableEnergy #DataCenters #GIS #Sustainability #Infrastructure #Brazil
