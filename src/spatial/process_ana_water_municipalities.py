#!/usr/bin/env python3
"""Create municipality-level ANA Q95 surface-water evidence.

This emits hydrological availability evidence only. It is not a final water
suitability score and does not imply permitted industrial supply.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

METRIC_CRS="EPSG:5880"

def wavg(values,weights):
    m=np.isfinite(values)&np.isfinite(weights)&(weights>0)
    return float(np.average(values[m],weights=weights[m])) if m.any() else np.nan

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--water",required=True); ap.add_argument("--municipalities",required=True)
    ap.add_argument("--out",default="step09_ana_municipality_surface_water_evidence.csv")
    ap.add_argument("--qa",default="step09_ana_water_qa.json")
    args=ap.parse_args()
    mun=gpd.read_file(args.municipalities); water=gpd.read_file(args.water)
    if mun.crs is None or water.crs is None: raise RuntimeError("Both inputs must have a CRS")
    code=next(c for c in ["CD_MUN","ibge_code"] if c in mun.columns)
    name=next(c for c in ["NM_MUN","municipality"] if c in mun.columns)
    state=next(c for c in ["SIGLA_UF","state"] if c in mun.columns)
    mun=mun[[code,name,state,"geometry"]].rename(columns={code:"ibge_code",name:"municipality",state:"state"})
    mun["ibge_code"]=mun["ibge_code"].astype(str)
    water["DISPQ95"]=pd.to_numeric(water["DISPQ95"],errors="coerce")
    water=water[water.geometry.notna()&~water.geometry.is_empty&water["DISPQ95"].notna()].copy()
    m=mun.to_crs(METRIC_CRS); w=water.to_crs(METRIC_CRS)
    m["geometry"]=m.geometry.make_valid(); w["geometry"]=w.geometry.make_valid()
    w2=w[["DISPQ95","ID","NMRIO","geometry"]].reset_index(names="water_index")
    pairs=gpd.sjoin(w2,m[["ibge_code","geometry"]],predicate="intersects",how="inner").reset_index(drop=True)
    geom_m=m.set_index("ibge_code").geometry; geom_w=w.geometry
    lengths=[]
    for wi,mc in zip(pairs["water_index"],pairs["ibge_code"]):
        lengths.append(geom_w.loc[wi].intersection(geom_m.loc[mc]).length/1000.0)
    pairs["reach_length_km"]=lengths; pairs=pairs[pairs["reach_length_km"]>0].copy()
    rows=[]
    for mc,g in pairs.groupby("ibge_code"):
        q=g["DISPQ95"].to_numpy(float); L=g["reach_length_km"].to_numpy(float)
        rows.append({"ibge_code":mc,"water_reach_count":int(len(g)),
          "water_reach_length_km":float(L.sum()),
          "water_q95_length_weighted_mean_m3s":wavg(q,L),
          "water_q95_median_m3s":float(np.nanmedian(q)),
          "water_q95_p90_m3s":float(np.nanpercentile(q,90)),
          "water_q95_max_m3s":float(np.nanmax(q)),
          "water_reach_km_q95_ge_1":float(L[q>=1].sum()),
          "water_reach_km_q95_ge_10":float(L[q>=10].sum()),
          "water_reach_km_q95_ge_100":float(L[q>=100].sum())})
    metrics=pd.DataFrame(rows)
    out=mun.drop(columns="geometry").merge(metrics,on="ibge_code",how="left")
    out["water_has_mapped_q95_reach"]=out["water_reach_count"].fillna(0).gt(0)
    for c in ["water_q95_length_weighted_mean_m3s","water_q95_max_m3s"]:
        out[c+"_percentile"]=out[c].rank(pct=True,method="average")
    out["water_hydrological_availability_evidence_index"]=(
        .5*out["water_q95_length_weighted_mean_m3s_percentile"]+.5*out["water_q95_max_m3s_percentile"])
    out["water_score_status"]="HYDROLOGICAL_EVIDENCE_ONLY_NOT_PERMITTED_SUPPLY"
    op=Path(args.out); op.parent.mkdir(parents=True,exist_ok=True); out.to_csv(op,index=False)
    qa={"municipalities":int(len(out)),
      "municipalities_with_mapped_q95_reach":int(out["water_has_mapped_q95_reach"].sum()),
      "municipalities_without_mapped_q95_reach":int((~out["water_has_mapped_q95_reach"]).sum()),
      "source_layer":"ANA/SNIRH Disponibilidade Hídrica Superficial","field":"DISPQ95",
      "interpretation":"Hydrological surface-water availability evidence only; not a water right, permit, utility commitment, sustainable withdrawal guarantee, or parcel-level feasibility result."}
    qp=Path(args.qa); qp.parent.mkdir(parents=True,exist_ok=True)
    qp.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(qa,indent=2,ensure_ascii=False))

if __name__=="__main__": main()
