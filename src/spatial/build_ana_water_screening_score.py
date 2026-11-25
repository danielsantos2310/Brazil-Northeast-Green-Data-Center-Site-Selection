#!/usr/bin/env python3
"""Build municipality hydrological-access screening evidence from ANA Q95.

Direct municipalities retain the direct ANA municipality Q95 index.
Municipalities without an intersecting Q95 reach use the nearest ANA reach:
nearest-reach Q95 percentile / (1 + distance_km / decay_km).

This is hydrological-access evidence only. It is not a water right, permitted
withdrawal, utility commitment, sustainable supply guarantee or cooling design.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

METRIC_CRS="EPSG:5880"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--direct-evidence",required=True)
    p.add_argument("--water-geometry",required=True)
    p.add_argument("--municipalities",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--decay-km",type=float,default=25.0)
    a=p.parse_args()

    direct=pd.read_csv(a.direct_evidence,dtype={"ibge_code":str})
    water=gpd.read_file(a.water_geometry)
    mun=gpd.read_file(a.municipalities)
    code=next(c for c in ["CD_MUN","ibge_code"] if c in mun.columns)
    mun[code]=mun[code].astype(str)
    water["DISPQ95"]=pd.to_numeric(water["DISPQ95"],errors="coerce")
    water=water[water["DISPQ95"].notna() & water.geometry.notna() & ~water.geometry.is_empty].copy()

    m=mun[[code,"geometry"]].to_crs(METRIC_CRS)
    w=water[["OBJECTID","DISPQ95","NMRIO","geometry"]].to_crs(METRIC_CRS)
    m["geometry"]=m.geometry.make_valid()
    w["geometry"]=w.geometry.make_valid()

    near=gpd.sjoin_nearest(
        m,
        w,
        how="left",
        distance_col="nearest_q95_reach_distance_m",
    )
    near["nearest_q95_reach_distance_km"]=near["nearest_q95_reach_distance_m"]/1000.0
    near=near.sort_values(
        [code,"nearest_q95_reach_distance_km","DISPQ95","OBJECTID"],
        ascending=[True,True,False,True],
    ).drop_duplicates(code)
    near=near[[code,"OBJECTID","DISPQ95","NMRIO","nearest_q95_reach_distance_km"]].rename(columns={
        code:"ibge_code",
        "OBJECTID":"nearest_q95_reach_objectid",
        "DISPQ95":"nearest_q95_reach_m3s",
        "NMRIO":"nearest_q95_reach_name",
    })

    all_q=np.sort(water["DISPQ95"].to_numpy(float))
    vals=near["nearest_q95_reach_m3s"].to_numpy(float)
    left=np.searchsorted(all_q,vals,side="left")
    right=np.searchsorted(all_q,vals,side="right")
    near["nearest_q95_reach_percentile_all_reaches"]=((left+right+1)/2)/len(all_q)

    out=direct.merge(near,on="ibge_code",how="left",validate="one_to_one")
    d=out["nearest_q95_reach_distance_km"].astype(float)
    fallback=out["nearest_q95_reach_percentile_all_reaches"]/(1+d/a.decay_km)
    out["water_hydrological_access_score"]=np.where(
        out["water_has_mapped_q95_reach"],
        out["water_hydrological_availability_evidence_index"],
        fallback,
    ).clip(0,1)
    out["water_score"]=out["water_hydrological_access_score"]
    out["water_distance_decay_scale_km"]=a.decay_km
    out["water_supply_verified"]=False
    out["water_current_demand_pressure_integrated"]=False
    out["water_evidence_confidence"]=np.select(
        [
            out["water_has_mapped_q95_reach"],
            (~out["water_has_mapped_q95_reach"]) & (d<=10),
            (~out["water_has_mapped_q95_reach"]) & (d<=25),
            (~out["water_has_mapped_q95_reach"]) & (d<=50),
        ],
        [
            "HIGH_LOCAL_Q95_INTERSECTION",
            "MEDIUM_NEARBY_Q95_LE10KM",
            "LOW_MEDIUM_NEARBY_Q95_10_25KM",
            "LOW_NEARBY_Q95_25_50KM",
        ],
        default="VERY_LOW_DISTANT_Q95_GT50KM",
    )
    out["water_score_status"]="HYDROLOGICAL_ACCESS_EVIDENCE_NOT_PERMITTED_SUPPLY"
    out["water_method"]="DIRECT_Q95_INDEX_ELSE_NEAREST_Q95_PERCENTILE_DISTANCE_DECAY"
    out["water_method_note"]="Direct: ANA municipality Q95 index. Fallback: nearest ANA Q95 reach percentile / (1 + distance_km/25). Hydrology only."

    if len(out)!=1794 or out["ibge_code"].nunique()!=1794:
        raise RuntimeError(f"Unexpected municipality coverage: rows={len(out)} unique={out['ibge_code'].nunique()}")
    dest=Path(a.out); dest.parent.mkdir(parents=True,exist_ok=True); out.to_csv(dest,index=False)
    print(out["water_evidence_confidence"].value_counts().to_string())
    print(f"wrote {len(out)} municipalities -> {dest}")

if __name__=="__main__":
    main()
