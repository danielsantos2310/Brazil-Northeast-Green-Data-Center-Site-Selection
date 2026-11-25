const scenarioSelect=document.getElementById('scenarioSelect');
const topN=document.getElementById('topN');
const candidateRows=document.getElementById('candidateRows');
const candidateDetail=document.getElementById('candidateDetail');
const leaders=document.getElementById('leaders');
const mapElement=document.getElementById('map');

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
  allGeo=g;candidates=c;scenarioTop=t;initMap();renderLeaders();renderCandidates();showDetail(candidates[0]);
  scenarioSelect.addEventListener('change',refreshMap);topN.addEventListener('change',refreshMap);
}).catch(e=>{mapElement.innerHTML=`<p style="padding:24px;color:#ffbd59">Data load failed: ${e.message}</p>`;});
