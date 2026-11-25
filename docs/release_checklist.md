# Release checklist — Northeast Brazil Green Data Centre Site Selection

## Required before public release

- [x] 1,794-municipality IBGE foundation validated.
- [x] ANEEL generation layer processed and QA'd.
- [x] EPE transmission/substation metrics processed.
- [x] ONS operating-grid and constrained-off context processed.
- [x] LABREN solar climatology processed by municipality.
- [x] Global Wind Atlas municipality metrics integrated.
- [x] ANATEL fibre/provider-diversity metrics integrated.
- [x] INMET climate normals upgraded to resolved station coordinates with conflict flags.
- [x] Scenario MCDA weights explicit and versioned.
- [x] 1,500-run sensitivity analysis deterministic and rerunnable.
- [x] External validation cases documented without feeding announced projects into the outcome.
- [x] REDATA/project due-diligence gates separated from municipality attractiveness.
- [x] Source registry and release manifest versioned.
- [ ] Extract current ANA Q95 spatial layer and aggregate municipality hydrological evidence.
- [ ] Add current demand-pressure context without using stale 2013/2014 demand data as if current.
- [ ] Refresh CNUC geometry from official July-2026 release and rerun environmental overlap.
- [ ] Rerun integrated feature table, four scenarios and 1,500-run sensitivity after water/CNUC updates.
- [ ] Decide whether recent INMET extreme-heat observations are needed as a separate resilience indicator.
- [ ] Freeze final Tier-A/B/C candidate sets.
- [ ] Refresh web-ready GeoJSON and website evidence assets from final model.
- [ ] Final QA: no legacy-v1 artifacts referenced by public website or README.
- [ ] Final copy edit and citations.
- [ ] User approval before GitHub push / GitHub Pages publication / LinkedIn publication.

## Never claim

- transmission proximity = available connection capacity;
- curtailed renewable energy = directly purchasable data-centre electricity;
- pipeline MW = firm available supply;
- fibre presence/provider count = physically redundant dark-fibre routes or SLA;
- Q95 hydrological availability = permitted/sustainable industrial water supply;
- municipality protected-area overlap = every parcel is prohibited;
- municipality ranking = investment-grade parcel selection;
- Low-Water AI ranking = final until water evidence is integrated.
