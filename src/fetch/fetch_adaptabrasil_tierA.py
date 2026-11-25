"""Fetch AdaptaBrasil municipal climate-risk indicators for the Tier-A shortlist.

Official API documentation:
https://github.com/AdaptaBrasil/AdaptaBrasilAPIAccess

The script discovers indicator IDs from the live hierarchy by name instead of
hardcoding them. This is deliberate because the official project notes that the
indicator structure is updated over time.

Outputs one row per Tier-A municipality and requested indicator.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
import requests

BASE = "https://sistema.adaptabrasil.mcti.gov.br/api"
HIERARCHY = f"{BASE}/hierarquia/adaptabrasil"
TIERA = Path("data/processed/step12_tierA_candidate_archetypes_and_gates_v4_water_integrated_2026-11-25.csv")
OUT = Path("data/processed/step16_adaptabrasil_tierA_risk_v1.csv")

TARGETS = {
    "water_stress_risk": [
        "índice de risco de impacto do estresse hídrico",
        "risco de impacto do estresse hídrico",
    ],
    "flood_risk": [
        "índice de risco de impacto para inundações, enxurradas e alagamentos",
        "índice de risco para inundações, enxurradas e alagamentos",
        "inundações, enxurradas e alagamentos",
    ],
}

STATE_BY_UF = {"BA":"BA","CE":"CE","PI":"PI","AL":"AL"}

def norm(s: object) -> str:
    s = "" if s is None else str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()

def walk(obj, path=()):
    if isinstance(obj, dict):
        yield path, obj
        for k, v in obj.items():
            yield from walk(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, path + (i,))

def text_blob(d: dict) -> str:
    vals=[]
    for k,v in d.items():
        if isinstance(v,(str,int,float)) and k.lower() in {
            "name","nome","title","titulo","simple_description","descricao_simples",
            "complete_description","descricao_completa"
        }:
            vals.append(str(v))
    return norm(" | ".join(vals))

def discover(hierarchy: object):
    found={}
    for key, aliases in TARGETS.items():
        best=None
        for path,node in walk(hierarchy):
            if not isinstance(node,dict):
                continue
            blob=text_blob(node)
            if not blob:
                continue
            score=max((len(norm(a)) if norm(a) in blob else 0) for a in aliases)
            if score<=0:
                continue
            ident=node.get("id") or node.get("indicator_id") or node.get("indicador")
            years=node.get("years") or node.get("anos") or node.get("year") or node.get("ano")
            if ident is None:
                continue
            candidate=(score, len(path), ident, years, blob)
            if best is None or candidate[0]>best[0] or (candidate[0]==best[0] and candidate[1]<best[1]):
                best=candidate
        if best is None:
            raise RuntimeError(f"Could not discover AdaptaBrasil indicator for {key}")
        found[key]={"id":best[2],"years":best[3],"label":best[4]}
    return found

def choose_year(years):
    if isinstance(years,list) and years:
        vals=[]
        for y in years:
            if isinstance(y,dict):
                y=y.get("year") or y.get("ano") or y.get("value")
            try: vals.append(int(y))
            except Exception: pass
        return max(vals) if vals else None
    try: return int(years)
    except Exception: return None

def fetch_indicator(uf, indicator_id, year):
    url=f"{BASE}/mapa-dados/{uf}/municipio/{indicator_id}/{year}/null/adaptabrasil"
    r=requests.get(url,timeout=60)
    r.raise_for_status()
    return r.json(), url

def extract_record(rec):
    code = rec.get("id") or rec.get("geocode") or rec.get("codigo") or rec.get("county_id")
    name = rec.get("name") or rec.get("nome") or rec.get("municipio")
    value = rec.get("value") or rec.get("valor")
    label = rec.get("rangelabel") or rec.get("faixa") or rec.get("label")
    if isinstance(value,str):
        value=value.replace(",",".")
    try: value=float(value)
    except Exception: value=None
    return code,name,value,label

def main():
    session=requests.Session()
    hierarchy=session.get(HIERARCHY,timeout=60)
    hierarchy.raise_for_status()
    h=hierarchy.json()
    indicators=discover(h)

    tiera=pd.read_csv(TIERA,dtype={"ibge_code":str})
    rows=[]

    for key,meta in indicators.items():
        year=choose_year(meta["years"])
        if year is None:
            raise RuntimeError(f"No usable year discovered for {key}: {meta}")
        for uf, group in tiera.groupby("state"):
            payload,url=fetch_indicator(STATE_BY_UF.get(uf,uf),meta["id"],year)
            if isinstance(payload,dict):
                data=payload.get("data") or payload.get("results") or payload.get("features") or []
            else:
                data=payload
            index={}
            for rec in data:
                if isinstance(rec,dict) and "properties" in rec:
                    rec=rec["properties"]
                code,name,value,label=extract_record(rec)
                if code is not None:
                    index[str(code)[:7]]=(name,value,label)
                if name:
                    index[norm(name.split("/")[0])]=(name,value,label)

            for _,m in group.iterrows():
                code=str(m["ibge_code"])[:7]
                val=index.get(code) or index.get(norm(m["municipality"]))
                rows.append({
                    "ibge_code":code,
                    "municipality":m["municipality"],
                    "state":uf,
                    "indicator_key":key,
                    "indicator_id":meta["id"],
                    "year":year,
                    "value":None if val is None else val[1],
                    "range_label":None if val is None else val[2],
                    "source_url":url,
                    "matched":val is not None,
                })

    out=pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(OUT,index=False)
    print(json.dumps(indicators,ensure_ascii=False,indent=2))
    print(out.to_string(index=False))
    print(f"Wrote {OUT}")

if __name__=="__main__":
    main()
