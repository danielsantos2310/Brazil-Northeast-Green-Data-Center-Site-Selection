const scenarioSelect=document.getElementById('scenarioSelect');
const topN=document.getElementById('topN');
const candidateRows=document.getElementById('candidateRows');
const candidateDetail=document.getElementById('candidateDetail');
const leaders=document.getElementById('leaders');
const mapElement=document.getElementById('map');

const diligenceSites=[
  {priority:1,name:'Bom Jesus da Lapa',state:'BA',status:'External diligence now',statusClass:'',summary:'Strong grid and hydrology evidence, zero municipality-level CNUC overlap, moderate flood-risk screening and active regional water-infrastructure reinforcement.',waterStress:0.67,waterLabel:'High',flood:0.47,floodLabel:'Medium',signal:'Adutora da Fé is a positive regional water-security signal, but it does not prove industrial allocation.',gates:['Formal utility load/headroom offer','Industrial water-right and supply study','Two physically independent fibre routes','Parcel title, flood, environment and geotechnical screen']},
  {priority:2,name:'Brumado',state:'BA',status:'External diligence now',statusClass:'',summary:'The strongest cooling-climate profile in the final group, clean municipality CNUC screening and medium baseline water-stress risk.',waterStress:0.45,waterLabel:'Medium',flood:0.75,floodLabel:'High',signal:'Cristalândia storage reinforcement is a positive water-security signal; high municipality-scale flood risk shifts attention to parcel selection.',gates:['Utility headroom and connection cost','Parcel flood and hydraulic assessment','Permitted industrial water source','Route-diverse fibre']},
  {priority:3,name:'Juazeiro',state:'BA',status:'Advance conditionally',statusClass:'conditional',summary:'Very strong Q95 evidence, renewable ecosystem and provider depth, but the São Francisco corridor also carries substantial competing water demand.',waterStress:0.83,waterLabel:'Very high',flood:0.76,floodLabel:'High',signal:'SAAE reports significant distribution losses and restructuring. Strong river flow cannot be treated as spare industrial water.',gates:['Industrial water allocation under competing basin demand','Formal utility headroom','Parcel flood and drainage design','Independent fibre-route validation']},
  {priority:4,name:'São Gonçalo do Amarante',state:'CE',status:'Strategic conditional',statusClass:'conditional',summary:'The strongest strategic digital-industrial hub case, with excellent connectivity and Pecém/ZPE context, but two blocking risks remain explicit.',waterStress:0.80,waterLabel:'Very high',flood:0.28,floodLabel:'Low',signal:'Low flood-risk screening is encouraging, but EPE access-risk evidence and very-high climate water stress must be resolved before promotion.',gates:['Resolve EPE connection timing and headroom','Industrial/reclaimed-water strategy','Independent carrier paths','Parcel environmental screen']},
  {priority:5,name:'Urandi',state:'BA',status:'Advance conditionally',statusClass:'conditional',summary:'Strong renewable-grid-climate balance and clean municipality CNUC screening, with moderate flood risk.',waterStress:0.62,waterLabel:'High',flood:0.46,floodLabel:'Medium',signal:'2026 municipal rationing is a real service-stress signal; a major new adductor remains a planned reinforcement rather than operating industrial supply.',gates:['Reliable industrial water source through dry-season conditions','Confirm reinforcement timing and firm capacity','Utility headroom','Fibre redundancy and parcel feasibility']}
];
const dossierList=document.getElementById('dossierList');
const dossierDetail=document.getElementById('dossierDetail');
const riskCompare=document.getElementById('riskCompare');


const scenarios={
  hyperscale_ai:{label:'Hyperscale AI',rank:'hyperscale_ai_rank_water_integrated',score:'hyperscale_ai_score_water_integrated'},
  colocation_digital_hub:{label:'Colocation / Digital Hub',rank:'colocation_digital_hub_rank_water_integrated',score:'colocation_digital_hub_score_water_integrated'},
  renewable_first_compute:{label:'Renewable-first Compute',rank:'renewable_first_compute_rank_water_integrated',score:'renewable_first_compute_score_water_integrated'},
  low_water_ai:{label:'Water-resilient AI',rank:'low_water_ai_rank_water_integrated',score:'low_water_ai_score_water_integrated'}
};
let map,geoLayer,allGeo,candidates=[],scenarioTop={};
const fmt=(v,d=2)=>v==null||Number.isNaN(Number(v))?'—':Number(v).toFixed(d);
const safe=v=>v==null?'—':v;
function colorForRank(r){if(r<=10)return'#39e6b2';if(r<=25)return'#65b9ff';if(r<=50)return'#8b9fff';if(r<=100)return'#b79cff';return'#415467'}
function styleFeature(f){
  const s=scenarios[scenarioSelect.value],rank=Number(f.properties[s.rank]),top=Number(topN.value),visible=rank<=top;
  return{color:'#0b1722',weight:.5,fillColor:colorForRank(rank),fillOpacity:visible?.76:.035,opacity:visible?.6:.1}
}
function popupHtml(p){
  const s=scenarios[scenarioSelect.value];
  return `<b>${p.municipality}, ${p.state}</b><br>${s.label}: rank <b>#${p[s.rank]}</b> · score ${fmt(p[s.score],3)}
  <br>Energy ${fmt(p.energy_score)} · Grid ${fmt(p.grid_strength_score)} · Fibre ${fmt(p.connectivity_score)}
  <br>Climate ${fmt(p.climate_score)} · Environment ${fmt(p.environment_score)} · Water ${fmt(p.water_score)}
  ${p.epe_known_near_term_access_constraint_flag?'<br>⚠ EPE near-term grid-access risk evidence':''}`;
}
function renderLeaders(){
  const slug=scenarioSelect.value,s=scenarios[slug],arr=(scenarioTop[slug]||[]).slice(0,5);
  leaders.innerHTML=arr.map(p=>`<div class="leader-card"><span>#${p[s.rank]}</span><b>${p.municipality}</b><small>${p.state} · ${fmt(p[s.score],3)}</small></div>`).join('');
}
function refreshMap(){geoLayer.setStyle(styleFeature);geoLayer.eachLayer(l=>l.bindPopup(popupHtml(l.feature.properties)));renderLeaders();renderCandidates()}
function initMap(){
  map=L.map('map').setView([-9.5,-40.8],5);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,attribution:'© OpenStreetMap'}).addTo(map);
  geoLayer=L.geoJSON(allGeo,{style:styleFeature,onEachFeature:(f,l)=>l.bindPopup(popupHtml(f.properties))}).addTo(map);
  map.fitBounds(geoLayer.getBounds(),{padding:[8,8]});
}

function candidateFor(name){return candidates.find(c=>c.municipality===name)}
function metricBar(label,value){
  const pct=Math.max(0,Math.min(100,Number(value||0)*100));
  return `<div class="dossier-metric"><label><span>${label}</span><b>${fmt(value)}</b></label><div class="dossier-track"><div class="dossier-fill" style="width:${pct}%"></div></div></div>`;
}
function focusDossierOnMap(name){
  if(!map||!geoLayer)return;
  let target=null;
  geoLayer.eachLayer(layer=>{if(layer.feature?.properties?.municipality===name)target=layer});
  if(target){
    const bounds=target.getBounds?target.getBounds():null;
    if(bounds)map.fitBounds(bounds,{padding:[40,40],maxZoom:9});
    if(target.openPopup)target.openPopup();
    document.getElementById('map-section')?.scrollIntoView({behavior:'smooth',block:'start'});
  }
}
function showDossier(site){
  const p=candidateFor(site.name)||{};
  document.querySelectorAll('.dossier-tab').forEach(b=>b.classList.toggle('active',b.dataset.site===site.name));
  dossierDetail.innerHTML=`
    <div class="dossier-top">
      <div><div class="dossier-kicker">Priority ${String(site.priority).padStart(2,'0')} · ${site.state}</div><h3>${site.name}</h3><p class="dossier-summary">${site.summary}</p></div>
      <div class="dossier-status ${site.statusClass}">${site.status}</div>
    </div>
    <div class="dossier-body">
      <div>
        <div class="dossier-section"><h4>Core screening profile</h4><div class="evidence-bars">${metricBar('Energy',p.energy_score)}${metricBar('Grid',p.grid_strength_score)}${metricBar('Connectivity',p.connectivity_score)}${metricBar('Climate',p.climate_score)}${metricBar('Environment',p.environment_score)}${metricBar('Water / hydrology',p.water_score)}</div></div>
        <div class="dossier-section"><h4>Public infrastructure signal</h4><div class="public-signal">${site.signal}</div></div>
      </div>
      <div>
        <div class="dossier-section"><h4>Climate-risk screening</h4><div class="risk-boxes"><div class="risk-box"><span>Water stress · baseline 2020</span><strong>${site.waterStress.toFixed(2)}</strong><small>${site.waterLabel}</small></div><div class="risk-box ${site.floodLabel==='Low'?'low':''}"><span>Flood / flash flood · 2015</span><strong>${site.flood.toFixed(2)}</strong><small>${site.floodLabel}</small></div></div></div>
        <div class="dossier-section"><h4>Blocking gates</h4><div class="gate-list">${site.gates.map(g=>`<div class="gate-item">${g}</div>`).join('')}</div></div>
      </div>
    </div>
    <div class="meta">
      <div><b>${safe(p.fiber_provider_count)}</b><span>recorded fibre providers</span></div>
      <div><b>${fmt(p.nearest_ons_operating_230kv_substation_distance_km,1)} km</b><span>nearest ONS ≥230 kV</span></div>
      <div><b>${fmt(p.cnuc_overlap_pct,1)}%</b><span>municipality CNUC overlap</span></div>
      <div><b>${fmt(p.sensitivity_median_rank_across_scenarios,1)}</b><span>median MC rank</span></div>
    </div>
    <div class="dossier-actions"><button class="dossier-action primary" type="button" data-focus-site="${site.name}">Show on map</button><a class="dossier-action" href="https://github.com/danielsantos2310/Brazil-Northeast-Green-Data-Center-Site-Selection/blob/main/docs/step16_external_diligence_brief.md" target="_blank" rel="noreferrer">Read diligence brief ↗</a></div>
    <p class="footnote">Municipality-scale evidence only. Utility capacity, permitted industrial water, physically independent carrier routes and parcel feasibility remain unverified external gates.</p>`;
  dossierDetail.querySelector('[data-focus-site]')?.addEventListener('click',()=>focusDossierOnMap(site.name));
}
function renderDossiers(){
  if(!dossierList||!dossierDetail)return;
  dossierList.innerHTML=diligenceSites.map(s=>`<button type="button" class="dossier-tab" data-site="${s.name}"><span class="dossier-tab-rank">${String(s.priority).padStart(2,'0')}</span><span><strong>${s.name}</strong><small>${s.status}</small></span><span class="dossier-tab-state">${s.state}</span></button>`).join('');
  dossierList.querySelectorAll('.dossier-tab').forEach(btn=>btn.addEventListener('click',()=>showDossier(diligenceSites.find(s=>s.name===btn.dataset.site))));
  showDossier(diligenceSites[0]);
  if(riskCompare)riskCompare.innerHTML=diligenceSites.map(s=>`<div class="risk-row"><b>${s.name}</b><div><div class="risk-label">Water stress</div><div class="risk-meter"><i style="width:${s.waterStress*100}%"></i></div></div><span class="risk-value">${s.waterStress.toFixed(2)}</span><div><div class="risk-label">Flood</div><div class="risk-meter flood"><i style="width:${s.flood*100}%"></i></div></div><span class="risk-value">${s.flood.toFixed(2)}</span></div>`).join('');
}

function renderCandidates(){
  const s=scenarios[scenarioSelect.value];
  const arr=[...candidates].sort((a,b)=>Number(a[s.rank])-Number(b[s.rank]));
  candidateRows.innerHTML='';
  arr.forEach(p=>{
    const tr=document.createElement('tr');
    tr.innerHTML=`<td><span class="rank">#${p[s.rank]}</span> ${p.municipality}, ${p.state}</td>
      <td>${p.candidate_archetype}</td><td>#${p[s.rank]}</td>
      <td>${fmt(p.sensitivity_median_rank_across_scenarios,1)}</td><td>${fmt(p.sensitivity_worst_p90_rank,0)}</td>`;
    tr.onclick=()=>showDetail(p);candidateRows.appendChild(tr);
  });
}
function bar(name,value){
  const pct=Math.max(0,Math.min(100,Number(value||0)*100));
  return `<div class="bar"><label><span>${name}</span><b>${fmt(value)}</b></label><div class="track"><div class="fill" style="width:${pct}%"></div></div></div>`;
}
function showDetail(p){
  candidateDetail.innerHTML=`<div class="place">${p.municipality}, ${p.state}</div>
    <div><span class="tag">${p.candidate_archetype}</span>${p.epe_known_near_term_access_constraint_flag?'<span class="tag warn">Grid-access risk flag</span>':''}</div>
    <div>${bar('Energy',p.energy_score)}${bar('Grid',p.grid_strength_score)}${bar('Connectivity',p.connectivity_score)}${bar('Climate',p.climate_score)}${bar('Environment',p.environment_score)}${bar('Water',p.water_score)}</div>
    <div class="meta">
      <div><b>${safe(p.fiber_provider_count)}</b><span>fibre providers</span></div>
      <div><b>${fmt(p.operating_wind_solar_mw,0)} MW</b><span>operating wind + solar</span></div>
      <div><b>${fmt(p.nearest_ons_operating_230kv_substation_distance_km,1)} km</b><span>nearest ONS ≥230 kV</span></div>
      <div><b>${fmt(p.cnuc_overlap_pct,1)}%</b><span>CNUC overlap</span></div>
    </div>
    ${p.zpe_name?`<p><b>${p.zpe_name}</b> · ${safe(p.zpe_status)}</p>`:''}
    <p class="footnote">Water evidence: <b>${safe(p.water_evidence_confidence)}</b> · permitted supply verified: <b>NO</b></p>
    <div class="decision-note"><p><b>Primary strengths</b><br>${p.primary_strengths}</p><p><b>Watch-outs</b><br>${p.key_watchouts}</p><p><b>Next gate</b><br>${p.recommended_next_gate}</p></div>
    <p class="footnote">Municipality screening only. Parcel feasibility, utility capacity, carrier-route independence, permitting and water rights require project-level due diligence.</p>`;
}
Promise.all([
  fetch('data/municipality_scores.geojson').then(r=>r.json()),
  fetch('data/tierA_candidates.json').then(r=>r.json()),
  fetch('data/scenario_top100.json').then(r=>r.json())
]).then(([g,c,t])=>{
  allGeo=g;candidates=c;scenarioTop=t;initMap();renderLeaders();renderCandidates();showDetail(candidates[0]);renderDossiers();
  scenarioSelect.addEventListener('change',refreshMap);topN.addEventListener('change',refreshMap);
}).catch(e=>{mapElement.innerHTML=`<p style="padding:24px;color:#ffbd59">Data load failed: ${e.message}</p>`;});
