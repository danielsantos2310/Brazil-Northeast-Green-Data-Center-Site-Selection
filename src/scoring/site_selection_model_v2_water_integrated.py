#!/usr/bin/env python3
"""Water-integrated municipality MCDA scorer."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

DIM={"energy":"energy_score","grid":"grid_strength_score","connectivity":"connectivity_score",
     "climate":"climate_score","environment":"environment_score",
     "strategic_context":"strategic_context_score","water":"water_score"}
SLUG={"Hyperscale AI":"hyperscale_ai","Colocation / digital hub":"colocation_digital_hub",
      "Renewable-first compute":"renewable_first_compute","Low-water AI":"low_water_ai"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--features",required=True,type=Path)
    p.add_argument("--weights",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    f=pd.read_csv(a.features,low_memory=False)
    w=pd.read_csv(a.weights)
    if "final_target_weight" not in w.columns: raise ValueError("weights need final_target_weight")
    for scen,sw in w.groupby("scenario",sort=False):
        if not np.isclose(sw["final_target_weight"].sum(),1.0): raise ValueError(f"{scen} weights do not sum to 1")
        vals=np.zeros(len(f))
        for _,r in sw.iterrows():
            col=DIM[r["dimension"]]
            x=pd.to_numeric(f[col],errors="coerce")
            if x.isna().any(): raise ValueError(f"{col} has missing values")
            vals += x.to_numpy(float)*float(r["final_target_weight"])
        slug=SLUG[scen]
        f[f"{slug}_score_water_integrated"]=vals
        f[f"{slug}_rank_water_integrated"]=pd.Series(vals).rank(method="min",ascending=False).astype(int).to_numpy()
    rank_cols=[f"{s}_rank_water_integrated" for s in SLUG.values()]
    f["scenario_mean_rank_water_integrated"]=f[rank_cols].mean(axis=1)
    f["scenario_rank_std_water_integrated"]=f[rank_cols].std(axis=1,ddof=0)
    f["scenario_top_50_frequency_water_integrated"]=(f[rank_cols]<=50).mean(axis=1)
    keep=["ibge_code","municipality","state","energy_score","grid_strength_score","connectivity_score",
          "climate_score","environment_score","strategic_context_score","water_score",
          "water_evidence_confidence","water_has_mapped_q95_reach","nearest_q95_reach_distance_km",
          "water_supply_verified"]
    for s in SLUG.values(): keep += [f"{s}_score_water_integrated",f"{s}_rank_water_integrated"]
    keep += ["scenario_mean_rank_water_integrated","scenario_rank_std_water_integrated","scenario_top_50_frequency_water_integrated"]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    f[keep].sort_values(["scenario_mean_rank_water_integrated","municipality"]).to_csv(a.output,index=False)

if __name__=="__main__":
    main()
