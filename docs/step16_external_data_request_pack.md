# Step 16 — External Data Request Pack

Use this pack for the five current external-diligence priorities:

1. Bom Jesus da Lapa, BA
2. Brumado, BA
3. Juazeiro, BA
4. São Gonçalo do Amarante / Pecém, CE
5. Urandi, BA

Parnaíba, PI should receive the same requests if promoted from reserve.

## A. Electricity / utility connection request

Request a formal pre-connection or feasibility response for at least three load cases: **50 MW, 100 MW and 200 MW**, unless the target project size is already known.

Required evidence:

- feasible point(s) of connection and voltage level;
- currently available firm capacity, if the utility is permitted to state it;
- connection queue / competing committed loads;
- required network reinforcements;
- expected study, permitting, procurement and energisation timeline;
- indicative customer-funded connection CAPEX;
- N-1 / redundancy options and independent supply paths;
- fault-level and protection constraints;
- reactive-power / power-factor requirements;
- planned transmission/substation works that materially affect the connection;
- whether staged energisation is possible;
- restrictions arising from EPE/ONS access studies;
- requirements for self-generation, PPAs or behind-the-meter assets;
- curtailment / interruption conditions applicable to the requested connection;
- validity period of any capacity indication.

**Do not accept:** transmission proximity, nominal substation voltage or renewable generation nearby as a substitute for a connection offer.

## B. Water / cooling-supply request

Evaluate at least two cooling architectures: a low-water design and a water-assisted design.

Required evidence:

- source(s) of raw/potable/industrial/reclaimed water;
- legally allocable industrial volume in m³/day;
- firm daily and peak-hour supply;
- existing treatment and transmission constraints;
- pressure and connection location;
- historical interruption/rationing record;
- drought-stage restrictions and priority-of-use rules;
- source-basin water-right status and remaining allocation, where publishable;
- raw-water quality and treatment requirements;
- wastewater/reclaimed-water availability and quality;
- discharge route and effluent requirements;
- cost structure for connection, treatment and consumption;
- planned system expansions and their funded/contracted status;
- whether the proposed data-centre demand can be served without reducing priority public supply.

**Do not accept:** Q95, reservoir presence or a municipal supply project as proof of industrial allocation.

## C. Fibre / carrier request

Provider count is only a discovery signal. Require physical-route evidence.

Required evidence:

- carrier and wholesale operator names;
- nearest PoPs / meet-me points;
- route maps to the candidate parcel;
- proof that proposed Route A and Route B do not share the same duct, bridge, pole corridor or aggregation node;
- dark-fibre availability, if applicable;
- wavelength / lit-service alternatives;
- expected latency to Fortaleza, Salvador, Recife and major international exits;
- subsea-cable / landing-station reachability where relevant;
- construction lead time;
- wayleave / right-of-way constraints;
- SLA, MTTR and maintenance model;
- diverse building-entry options;
- pricing for scalable capacity tiers.

**Do not accept:** multiple retail brands using the same physical path as route diversity.

## D. Parcel request

Target enough parcels to preserve competition; do not start with a single preferred plot.

Required evidence:

- polygon / coordinates and gross/net developable area;
- ownership and title chain;
- zoning and permitted industrial use;
- municipal/state environmental restrictions;
- CNUC and other conservation constraints;
- floodplain, drainage and historical inundation evidence;
- geotechnical baseline and earthworks constraints;
- topography / slope;
- access-road capacity and abnormal-load route;
- distance to power and fibre connection points;
- water/sewer connection points;
- aviation, military, heritage or easement constraints;
- adjacent hazardous industry / pipeline / fuel-storage risk;
- expansion land;
- indicative land price and acquisition structure.

## E. Minimum pass/fail gates

A candidate cannot advance to parcel recommendation until:

1. **Power:** a credible connection path and schedule exists for the target MW.
2. **Water:** a legally and physically feasible cooling-water strategy exists, including a low-water option.
3. **Fibre:** two physically independent routes are evidenced.
4. **Parcel:** at least one viable parcel clears initial title, zoning, environment and flood screening.

## F. Information-quality labels

Use these labels for every response:

- `VERIFIED_FORMAL` — signed/official study, offer, licence, permit or engineering document.
- `VERIFIED_PUBLIC` — current official public dataset/document.
- `INDICATIVE_PROVIDER` — written but non-binding provider indication.
- `SECONDARY` — reputable secondary source.
- `ASSUMPTION` — modelling assumption only.
- `UNKNOWN` — no usable evidence.

Only `VERIFIED_FORMAL` can close utility-capacity, water-right, route-diversity or parcel-legal gates.

## G. Candidate-specific first questions

### Bom Jesus da Lapa
- What large-load connection options exist near the strongest grid nodes identified by the model?
- Can an industrial water demand be permitted without relying on public-supply capacity intended for human consumption?
- Which carriers can evidence two independent routes?

### Brumado
- What capacity and connection timeline can be offered near the identified grid infrastructure?
- Which parcels avoid the municipality-scale flood-risk concern?
- What water supply remains firm before and after the Cristalândia expansion?

### Juazeiro
- How would a large industrial allocation interact with existing São Francisco demand and irrigation use?
- Can the connection be served independently of current SAAE distribution losses?
- Which parcels have acceptable flood/drainage characteristics?

### São Gonçalo do Amarante / Pecém
- What specific network works/timing are required to overcome the current EPE access constraint?
- What reclaimed/industrial-water options are available for a low-WUE design?
- Can the Pecém carrier ecosystem provide physically independent routes?

### Urandi
- What source can provide industrial water during dry-season public rationing conditions?
- When would the proposed new adductor become operational and what firm capacity would it add?
- Is carrier-route diversity commercially achievable?

## H. Decision output

For each municipality, produce one signed-off gate sheet:

`POWER: PASS / CONDITIONAL / FAIL / UNKNOWN`  
`WATER: PASS / CONDITIONAL / FAIL / UNKNOWN`  
`FIBRE: PASS / CONDITIONAL / FAIL / UNKNOWN`  
`PARCEL: PASS / CONDITIONAL / FAIL / UNKNOWN`

Only candidates with no `FAIL` and no critical `UNKNOWN` proceed to investment economics.
