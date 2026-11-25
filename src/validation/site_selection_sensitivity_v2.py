#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

DIM_COLS={"energy":"energy_score","grid":"grid_strength_score","connectivity":"connectivity_score","climate":"climate_score","environment":"environment_score","strategic_context":"strategic_context_score","water":"water_score"}
SLUGS={"Hyperscale AI":"hyperscale_ai","Colocation / digital hub":"colocation_digital_hub","Renewable-first compute":"renewable_first_compute","Low-water AI":"low_water_ai"}
def rank_matrix(scores):
    order=np.argsort(-scores,axis=0,kind="mergesort"); ranks=np.empty_like(order,dtype=np.int32); cols=np.arange(scores.shape[1])
    ranks[order,cols]=np.arange(1,scores.shape[0]+1)[:,None]; return ranks
def main():
    p=argparse.ArgumentParser(); p.add_argument("--features",type=Path,required=True); p.add_argument("--weights",type=Path,required=True)
    p.add_argument("--mc-output",type=Path,required=True); p.add_argument("--shortlist-output",type=Path,required=True); p.add_argument("--qa-output",type=Path,required=True)
    p.add_argument("--iterations",type=int,default=1500); p.add_argument("--sigma",type=float,default=.20); p.add_argument("--seed",type=int,default=20261124); a=p.parse_args()
    f=pd.read_csv(a.features,low_memory=False); w=pd.read_csv(a.weights); rng=np.random.default_rng(a.seed); parts=[]; deterministic={}
    for scen,sw in w.groupby("scenario",sort=False):
        slug=SLUGS[scen]; active=sw[sw.provisional_no_water_weight>0].copy(); dims=active.dimension.tolist(); basew=active.provisional_no_water_weight.to_numpy(float)
        X=np.column_stack([pd.to_numeric(f[DIM_COLS[d]],errors="raise").to_numpy(float) for d in dims])
        W=rng.lognormal(mean=0.0,sigma=a.sigma,size=(a.iterations,len(dims)))*basew[None,:]; W=W/W.sum(axis=1,keepdims=True)
        scores=X@W.T; ranks=rank_matrix(scores); part=f[["ibge_code","municipality","state"]].copy(); part["scenario"]=scen
        part["mc_median_rank"]=np.median(ranks,axis=1); part["mc_p10_rank"]=np.percentile(ranks,10,axis=1); part["mc_p90_rank"]=np.percentile(ranks,90,axis=1)
        part["mc_top20_frequency"]=(ranks<=20).mean(axis=1); part["mc_top50_frequency"]=(ranks<=50).mean(axis=1)
        part["mc_top_decile_frequency"]=(ranks<=int(np.ceil(len(f)*.10))).mean(axis=1); part["mc_score_mean"]=scores.mean(axis=1); part["mc_score_sd"]=scores.std(axis=1); parts.append(part)
        br=pd.Series(X@basew).rank(method="min",ascending=False).astype(int).to_numpy(); nw=basew.copy()
        if "strategic_context" in dims: j=dims.index("strategic_context"); nw[j]=0; nw/=nw.sum()
        nr=pd.Series(X@nw).rank(method="min",ascending=False).astype(int).to_numpy(); Xh=X.copy()
        if "grid" in dims:
            j=dims.index("grid"); risk=f["epe_known_near_term_access_constraint_flag"].fillna(False).astype(bool).to_numpy(); Xh[risk,j]*=.75
        hr=pd.Series(Xh@basew).rank(method="min",ascending=False).astype(int).to_numpy(); deterministic[scen]=(br,nr,hr)
    mc=pd.concat(parts,ignore_index=True); a.mc_output.parent.mkdir(parents=True,exist_ok=True); mc.to_csv(a.mc_output,index=False)
    agg=mc.groupby(["ibge_code","municipality","state"],as_index=False).agg(sensitivity_median_rank_across_scenarios=("mc_median_rank","mean"),sensitivity_worst_p90_rank=("mc_p90_rank","max"),sensitivity_mean_top20_frequency=("mc_top20_frequency","mean"),sensitivity_mean_top50_frequency=("mc_top50_frequency","mean"),sensitivity_mean_top_decile_frequency=("mc_top_decile_frequency","mean"))
    A=(agg.sensitivity_median_rank_across_scenarios<=25)&(agg.sensitivity_worst_p90_rank<=80)&(agg.sensitivity_mean_top50_frequency>=.85); B=agg.sensitivity_mean_top50_frequency>=.5; C=agg.sensitivity_mean_top_decile_frequency>=.75
    agg["robustness_tier"]=np.select([A,B,C],["A_robust_top_candidate","B_robust_shortlist","C_broad_top_decile"],"not_robust")
    attach=["ibge_code","energy_score","grid_strength_score","connectivity_score","climate_score","environment_score","strategic_context_score","fiber_provider_count","operating_wind_solar_mw","nearest_ons_operating_230kv_substation_distance_km","cnuc_overlap_pct","climate_evidence_confidence","zpe_name","zpe_status","epe_known_near_term_access_constraint_flag","ons_curtailment_pressure_signal","water_score_status"]
    agg=agg.merge(f[attach],on="ibge_code",how="left",validate="one_to_one")
    for scen,(br,nr,hr) in deterministic.items():
        slug=SLUGS[scen]; tmp=pd.DataFrame({"ibge_code":f.ibge_code,f"{slug}_rank_provisional_no_water":br,f"{slug}_rank_no_strategic_context":nr,f"{slug}_rank_grid_access_haircut_25pct":hr}); agg=agg.merge(tmp,on="ibge_code",how="left",validate="one_to_one")
    tiers=agg[agg.robustness_tier!="not_robust"].copy(); order={"A_robust_top_candidate":0,"B_robust_shortlist":1,"C_broad_top_decile":2}; tiers["_tier_order"]=tiers.robustness_tier.map(order)
    tiers=tiers.sort_values(["_tier_order","sensitivity_median_rank_across_scenarios","municipality"]).drop(columns="_tier_order"); a.shortlist_output.parent.mkdir(parents=True,exist_ok=True); tiers.to_csv(a.shortlist_output,index=False)
    qa={"iterations_per_scenario":a.iterations,"weight_noise":"multiplicative lognormal","sigma":a.sigma,"seed":a.seed,"tier_counts":agg.robustness_tier.value_counts().to_dict(),"tier_A":tiers.loc[tiers.robustness_tier=="A_robust_top_candidate","municipality"].tolist(),"notes":["Water remains excluded; active weights are provisional no-water weights.","Strategic-context zeroing is an anti-circularity stress test.","25% grid haircut is a scenario stress only for EPE-documented near-term access-risk municipalities; it is not an estimate of headroom."]}
    a.qa_output.parent.mkdir(parents=True,exist_ok=True); a.qa_output.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__": main()
