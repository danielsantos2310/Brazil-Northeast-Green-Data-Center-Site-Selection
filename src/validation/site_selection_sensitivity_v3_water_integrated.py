#!/usr/bin/env python3
"""Joint sensitivity: scenario weights + water fallback distance-decay uncertainty."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

DIM={"energy":"energy_score","grid":"grid_strength_score","connectivity":"connectivity_score",
     "climate":"climate_score","environment":"environment_score",
     "strategic_context":"strategic_context_score","water":"water_score"}

def rank_matrix(scores):
    order=np.argsort(-scores,axis=0,kind="mergesort")
    ranks=np.empty_like(order,dtype=np.int32); cols=np.arange(scores.shape[1])
    ranks[order,cols]=np.arange(1,scores.shape[0]+1)[:,None]
    return ranks

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--features",required=True,type=Path)
    p.add_argument("--weights",required=True,type=Path)
    p.add_argument("--mc-output",required=True,type=Path)
    p.add_argument("--shortlist-output",required=True,type=Path)
    p.add_argument("--qa-output",required=True,type=Path)
    p.add_argument("--iterations",type=int,default=1500)
    p.add_argument("--sigma",type=float,default=.20)
    p.add_argument("--seed",type=int,default=20261125)
    p.add_argument("--water-decay-min-km",type=float,default=15)
    p.add_argument("--water-decay-max-km",type=float,default=60)
    a=p.parse_args()

    f=pd.read_csv(a.features,low_memory=False)
    w=pd.read_csv(a.weights)
    rng=np.random.default_rng(a.seed)
    direct=f["water_has_mapped_q95_reach"].fillna(False).to_numpy(bool)
    direct_score=f["water_score"].fillna(0).to_numpy(float)
    near_pct=f["nearest_q95_reach_percentile_all_reaches"].fillna(0).to_numpy(float)
    near_dist=f["nearest_q95_reach_distance_km"].fillna(np.inf).to_numpy(float)
    n=len(f); parts=[]
    for scen,sw in w.groupby("scenario",sort=False):
        dims=sw["dimension"].tolist(); base=sw["final_target_weight"].to_numpy(float)
        W=rng.lognormal(0,a.sigma,size=(a.iterations,len(dims)))*base[None,:]
        W/=W.sum(axis=1,keepdims=True)
        decay=np.exp(rng.uniform(np.log(a.water_decay_min_km),np.log(a.water_decay_max_km),size=a.iterations))
        scores=np.zeros((n,a.iterations))
        for j,dim in enumerate(dims):
            if dim=="water":
                ws=np.where(direct[:,None],direct_score[:,None],near_pct[:,None]/(1+near_dist[:,None]/decay[None,:]))
                scores += ws*W[:,j][None,:]
            else:
                scores += f[DIM[dim]].to_numpy(float)[:,None]*W[:,j][None,:]
        ranks=rank_matrix(scores)
        p2=f[["ibge_code","municipality","state"]].copy(); p2["scenario"]=scen
        p2["mc_median_rank"]=np.median(ranks,axis=1)
        p2["mc_p90_rank"]=np.percentile(ranks,90,axis=1)
        p2["mc_top20_frequency"]=(ranks<=20).mean(axis=1)
        p2["mc_top50_frequency"]=(ranks<=50).mean(axis=1)
        p2["mc_top_decile_frequency"]=(ranks<=int(np.ceil(n*.10))).mean(axis=1)
        parts.append(p2)
    mc=pd.concat(parts,ignore_index=True); a.mc_output.parent.mkdir(parents=True,exist_ok=True); mc.to_csv(a.mc_output,index=False)
    agg=mc.groupby(["ibge_code","municipality","state"],as_index=False).agg(
        sensitivity_median_rank_across_scenarios=("mc_median_rank","mean"),
        sensitivity_worst_p90_rank=("mc_p90_rank","max"),
        sensitivity_mean_top20_frequency=("mc_top20_frequency","mean"),
        sensitivity_mean_top50_frequency=("mc_top50_frequency","mean"),
        sensitivity_mean_top_decile_frequency=("mc_top_decile_frequency","mean"))
    A=(agg.sensitivity_median_rank_across_scenarios<=25)&(agg.sensitivity_worst_p90_rank<=80)&(agg.sensitivity_mean_top50_frequency>=.85)
    B=agg.sensitivity_mean_top50_frequency>=.5; C=agg.sensitivity_mean_top_decile_frequency>=.75
    agg["robustness_tier"]=np.select([A,B,C],["A_robust_top_candidate","B_robust_shortlist","C_broad_top_decile"],"not_robust")
    tiers=agg[agg.robustness_tier!="not_robust"].copy()
    order={"A_robust_top_candidate":0,"B_robust_shortlist":1,"C_broad_top_decile":2}
    tiers["_o"]=tiers.robustness_tier.map(order)
    tiers=tiers.sort_values(["_o","sensitivity_median_rank_across_scenarios","municipality"]).drop(columns="_o")
    a.shortlist_output.parent.mkdir(parents=True,exist_ok=True); tiers.to_csv(a.shortlist_output,index=False)
    qa={"iterations_per_scenario":a.iterations,"weight_sigma":a.sigma,"seed":a.seed,
        "water_decay_km_range":[a.water_decay_min_km,a.water_decay_max_km],
        "tier_counts":agg.robustness_tier.value_counts().to_dict(),
        "tier_A":tiers.loc[tiers.robustness_tier=="A_robust_top_candidate",["municipality","state"]].to_dict("records"),
        "interpretation":"Joint scenario-weight and water-distance-method uncertainty; hydrology only, not permitted supply."}
    a.qa_output.parent.mkdir(parents=True,exist_ok=True)
    a.qa_output.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
