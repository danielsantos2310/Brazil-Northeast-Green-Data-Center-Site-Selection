"""Fetch AdaptaBrasil future climate-risk scenarios for Tier-A municipalities.

This keeps projected 2030/2050 risk separate from the baseline Step-16 gate
matrix. Scenario IDs and labels are discovered from the official live hierarchy;
nothing is hardcoded except the target indicator names.
"""

from __future__ import annotations
import re
import unicodedata
from pathlib import Path
import pandas as pd
import requests

BASE="https://sistema.adaptabrasil.mcti.gov.br/api"
HIER=f"{BASE}/hierarquia/adaptabrasil"
TIERA=Path("data/processed/step12_tierA_candidate_archetypes_and_gates_v4_water_integrated_2026-11-25.csv")
OUT=Path("data/processed/step16_adaptabrasil_tierA_future_risk_v1.csv")

TARGET_ALIASES={
 "water_stress_risk":["índice de risco de impacto do estresse hídrico","risco de impacto do estresse hídrico"],
 "flood_risk":["índice de risco para inundações, enxurradas e alagamentos","inundações, enxurradas e alagamentos"],
}

def norm(x):
    x=unicodedata.normalize("NFKD",str(x or "")).encode("ascii","ignore").decode()
    return re.sub(r"\s+"," ",x).strip().lower()

def discover(hierarchy,key,aliases):
    best=None
    for node in hierarchy:
        if not isinstance(node,dict): continue
        blob=norm(" | ".join(str(node.get(k) or "") for k in ["name","simple_description","complete_description"]))
        score=max([len(norm(a)) if norm(a) in blob else 0 for a in aliases])
        if score and (best is None or score>best[0]):
            best=(score,node)
    if best is None: raise RuntimeError(f"Indicator not found: {key}")
    return best[1]

def scenario_id(s):
    if isinstance(s,dict):
        return s.get("id") or s.get("scenario_id") or s.get("value")
    return s

def scenario_label(s):
    if isinstance(s,dict):
        return s.get("label") or s.get("name") or str(scenario_id(s))
    return str(s)

def extract(payload):
    rows=[]
    for rec in payload if isinstance(payload,list) else payload.get("data",[]):
        if "properties" in rec: rec=rec["properties"]
        rows.append({
          "ibge_code":str(rec.get("geocod_ibge") or rec.get("geocode") or rec.get("codigo") or "")[:7],
          "municipality_api":rec.get("name") or rec.get("nome"),
          "value":rec.get("value") or rec.get("valor"),
          "range_label":rec.get("rangelabel") or rec.get("label") or rec.get("faixa"),
        })
    return pd.DataFrame(rows)

def main():
    session=requests.Session()
    hierarchy=session.get(HIER,timeout=60).json()
    tiera=pd.read_csv(TIERA,dtype={"ibge_code":str})
    out=[]

    for key,aliases in TARGET_ALIASES.items():
        node=discover(hierarchy,key,aliases)
        iid=node["id"]
        years=node.get("years") or []
        if isinstance(years,str): years=[int(x) for x in years.split(",") if x.strip()]
        years=sorted(int(y) for y in years)
        baseline=years[0]
        future=[y for y in years if y>baseline]
        scenarios=node.get("scenarios") or []
        if not scenarios:
            raise RuntimeError(f"No future scenarios exposed for {key}")

        for year in future:
            for scen in scenarios:
                sid=scenario_id(scen)
                label=scenario_label(scen)
                for uf,group in tiera.groupby("state"):
                    url=f"{BASE}/mapa-dados/{uf}/municipio/{iid}/{year}/{sid}/adaptabrasil"
                    resp=session.get(url,timeout=60)
                    resp.raise_for_status()
                    frame=extract(resp.json())
                    idx=frame.set_index("ibge_code") if not frame.empty else pd.DataFrame()
                    for _,m in group.iterrows():
                        code=str(m["ibge_code"])[:7]
                        matched=not frame.empty and code in idx.index
                        rec=idx.loc[code] if matched else None
                        if isinstance(rec,pd.DataFrame): rec=rec.iloc[0]
                        out.append({
                          "ibge_code":code,"municipality":m["municipality"],"state":uf,
                          "indicator_key":key,"indicator_id":iid,"year":year,
                          "scenario_id":sid,"scenario_label":label,
                          "value":None if rec is None else rec["value"],
                          "range_label":None if rec is None else rec["range_label"],
                          "matched":matched,"source_url":url,
                        })

    df=pd.DataFrame(out)
    if not df["matched"].all():
        raise RuntimeError("One or more future AdaptaBrasil municipality matches failed.")
    OUT.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(OUT,index=False)
    print(df.to_string(index=False))
    print(f"Wrote {OUT}")

if __name__=="__main__":
    main()
