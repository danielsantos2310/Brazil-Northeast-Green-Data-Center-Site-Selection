#!/usr/bin/env python3
"""Provisional municipality MCDA scorer for the Northeast Brazil Green Data Centre project."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

DIMENSION_COLUMNS={"energy":"energy_score","grid":"grid_strength_score","connectivity":"connectivity_score",
"climate":"climate_score","environment":"environment_score","strategic_context":"strategic_context_score","water":"water_score"}
SCENARIO_SLUGS={"Hyperscale AI":"hyperscale_ai","Colocation / digital hub":"colocation_digital_hub",
"Renewable-first compute":"renewable_first_compute","Low-water AI":"low_water_ai"}

def load_weights(path:Path)->pd.DataFrame:
    w=pd.read_csv(path); required={"scenario","dimension","final_target_weight","provisional_no_water_weight","water_pending"}
    missing=required-set(w.columns)
    if missing: raise ValueError(f"Weight file missing columns: {sorted(missing)}")
    unknown=sorted(set(w["dimension"])-set(DIMENSION_COLUMNS))
    if unknown: raise ValueError(f"Unknown dimensions in weight file: {unknown}")
    return w

def score(features:pd.DataFrame,weights:pd.DataFrame)->pd.DataFrame:
    out=features.copy(); required={"ibge_code","municipality","state"}
    for dim in weights.loc[weights["provisional_no_water_weight"]>0,"dimension"].unique(): required.add(DIMENSION_COLUMNS[dim])
    missing=required-set(out.columns)
    if missing: raise ValueError(f"Feature table missing columns: {sorted(missing)}")
    for scenario,sw in weights.groupby("scenario",sort=False):
        slug=SCENARIO_SLUGS[scenario]; active=sw[sw["provisional_no_water_weight"]>0].copy()
        total=active["provisional_no_water_weight"].sum()
        if not np.isclose(total,1.0,atol=1e-6): raise ValueError(f"{scenario}: provisional weights sum to {total}")
        vals=np.zeros(len(out),dtype=float)
        for _,row in active.iterrows():
            col=DIMENSION_COLUMNS[row["dimension"]]; x=pd.to_numeric(out[col],errors="coerce")
            if x.isna().any(): raise ValueError(f"{scenario}: {col} has {int(x.isna().sum())} missing values")
            vals+=x.to_numpy()*float(row["provisional_no_water_weight"])
        sc=f"{slug}_score_provisional_no_water"; rc=f"{slug}_rank_provisional_no_water"
        out[sc]=vals; out[rc]=pd.Series(vals).rank(method="min",ascending=False).astype(int).to_numpy()
    rank_cols=[f"{s}_rank_provisional_no_water" for s in SCENARIO_SLUGS.values()]
    out["scenario_mean_rank_provisional"]=out[rank_cols].mean(axis=1)
    out["scenario_rank_std_provisional"]=out[rank_cols].std(axis=1,ddof=0)
    out["scenario_top_50_frequency"]=(out[rank_cols]<=50).mean(axis=1)
    out["scenario_top_decile_frequency"]=(out[rank_cols]<=max(1,int(np.ceil(len(out)*.10)))).mean(axis=1)
    return out

def validate(scored:pd.DataFrame,reference_path:Path)->dict:
    ref=pd.read_csv(reference_path); merged=scored.merge(ref,on=["ibge_code"],suffixes=("_calc","_ref"),validate="one_to_one"); checks={}
    for slug in SCENARIO_SLUGS.values():
        sc=f"{slug}_score_provisional_no_water"; rc=f"{slug}_rank_provisional_no_water"
        diff=np.abs(merged[f"{sc}_calc"]-merged[f"{sc}_ref"]); eq=merged[f"{rc}_calc"].astype(int).eq(merged[f"{rc}_ref"].astype(int))
        checks[slug]={"max_abs_score_difference":float(diff.max()),"rank_match_count":int(eq.sum()),"row_count":int(len(merged)),"all_ranks_match":bool(eq.all())}
    return checks

def main():
    p=argparse.ArgumentParser(); p.add_argument("--features",required=True,type=Path); p.add_argument("--weights",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path); p.add_argument("--validate-against",type=Path); p.add_argument("--validation-json",type=Path); a=p.parse_args()
    f=pd.read_csv(a.features); w=load_weights(a.weights); s=score(f,w)
    keep=["ibge_code","municipality","state","energy_score","grid_strength_score","connectivity_score","climate_score","environment_score","strategic_context_score","water_score_status"]
    for slug in SCENARIO_SLUGS.values(): keep += [f"{slug}_score_provisional_no_water",f"{slug}_rank_provisional_no_water"]
    keep += ["scenario_mean_rank_provisional","scenario_rank_std_provisional","scenario_top_decile_frequency","scenario_top_50_frequency"]
    a.output.parent.mkdir(parents=True,exist_ok=True); s[keep].sort_values(["scenario_mean_rank_provisional","municipality"]).to_csv(a.output,index=False)
    if a.validate_against:
        report=validate(s,a.validate_against); print(json.dumps(report,indent=2,ensure_ascii=False))
        if a.validation_json: a.validation_json.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__": main()
