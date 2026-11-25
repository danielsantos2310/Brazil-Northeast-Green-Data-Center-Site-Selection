#!/usr/bin/env python3
"""Aggregate CNUC protected-area geometry to IBGE municipalities.

The result is a municipality-level screening constraint, not parcel-level legal
advice. Integral Protection overlap flags a due-diligence issue; it does not imply
that the whole municipality is unavailable.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.errors import GEOSException
from shapely import make_valid

METRIC_CRS="EPSG:5880"

def pick_shp(path:Path)->Path:
    if path.is_file() and path.suffix.lower()==".shp":
        return path
    candidates=[p for p in path.rglob("*.shp") if "ponto" not in p.name.lower()]
    if not candidates:
        raise FileNotFoundError(f"No polygon .shp found under {path}")
    return max(candidates,key=lambda p:p.stat().st_size)

def safe_intersection(a,b):
    try:
        return a.intersection(b)
    except GEOSException:
        return make_valid(a).intersection(make_valid(b))

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--cnuc",required=True)
    ap.add_argument("--municipalities",required=True)
    ap.add_argument("--out",default="data/processed/cnuc_municipality_constraints.csv")
    ap.add_argument("--qa",default="outputs/qa/cnuc_municipality_qa.json")
    args=ap.parse_args()

    mun=gpd.read_file(args.municipalities)
    shp=pick_shp(Path(args.cnuc))
    try:
        uc=gpd.read_file(shp)
    except UnicodeDecodeError:
        uc=gpd.read_file(shp,encoding="ISO-8859-1")
    if mun.crs is None or uc.crs is None:
        raise RuntimeError("Missing CRS")

    code=next(c for c in ["CD_MUN","ibge_code"] if c in mun.columns)
    name=next(c for c in ["NM_MUN","municipality"] if c in mun.columns)
    state=next(c for c in ["SIGLA_UF","state"] if c in mun.columns)
    cols=[code,name,state]+(["AREA_KM2"] if "AREA_KM2" in mun.columns else [])+["geometry"]
    m=mun[cols].rename(columns={code:"CD_MUN",name:"NM_MUN",state:"SIGLA_UF"}).copy()
    m["CD_MUN"]=m["CD_MUN"].astype(str)

    group_col=next((c for c in ["grupo","GRUPO","grupo_manejo","Grupo"] if c in uc.columns),None)
    if not group_col:
        raise RuntimeError(f"Could not find CNUC group field. Columns: {list(uc.columns)}")
    uc[group_col]=uc[group_col].fillna("").astype(str)
    uc=uc[uc.geometry.notna() & ~uc.geometry.is_empty].copy()

    mm=m.to_crs(METRIC_CRS)
    uu=uc.to_crs(METRIC_CRS)
    mm["geometry"]=mm.geometry.make_valid()
    uu["geometry"]=uu.geometry.make_valid()
    mm["municipality_geometry_area_km2"]=mm.geometry.area/1e6

    pairs=gpd.sjoin(
        uu[[group_col,"geometry"]].reset_index(names="uc_index"),
        mm[["CD_MUN","geometry"]],
        predicate="intersects",
        how="inner",
    ).reset_index(drop=True)

    mgeom=mm.set_index("CD_MUN").geometry
    ugeom=uu.geometry
    rec=[]
    for r in pairs.itertuples(index=False):
        inter=safe_intersection(ugeom.loc[r.uc_index],mgeom.loc[r.CD_MUN])
        if inter.is_empty:
            continue
        a=inter.area/1e6
        if a>0:
            rec.append((str(r.CD_MUN),int(r.uc_index),str(getattr(r,group_col)),float(a),inter))

    by={}
    for cd,ui,grp,a,geom in rec:
        by.setdefault(cd,[]).append((ui,grp,a,geom))

    rows=[]
    for cd,items in by.items():
        union=gpd.GeoSeries([x[3] for x in items],crs=METRIC_CRS).union_all()
        pi=[x for x in items if "prote" in x[1].lower() and "integr" in x[1].lower()]
        us=[x for x in items if "uso" in x[1].lower() and "sust" in x[1].lower()]
        piu=gpd.GeoSeries([x[3] for x in pi],crs=METRIC_CRS).union_all() if pi else None
        usu=gpd.GeoSeries([x[3] for x in us],crs=METRIC_CRS).union_all() if us else None
        rows.append({
            "CD_MUN":cd,
            "cnuc_uc_count":len(set(x[0] for x in items)),
            "cnuc_piece_area_sum_km2":sum(x[2] for x in items),
            "cnuc_protecao_integral_count":len(set(x[0] for x in pi)),
            "cnuc_uso_sustentavel_count":len(set(x[0] for x in us)),
            "cnuc_union_area_km2":union.area/1e6,
            "cnuc_protecao_integral_area_km2":0.0 if piu is None else piu.area/1e6,
            "cnuc_uso_sustentavel_area_km2":0.0 if usu is None else usu.area/1e6,
        })

    met=pd.DataFrame(rows)
    out=mm.drop(columns="geometry").merge(met,on="CD_MUN",how="left")
    metric_cols=[c for c in met.columns if c!="CD_MUN"]
    out[metric_cols]=out[metric_cols].fillna(0)
    denom=out["municipality_geometry_area_km2"].replace(0,np.nan)
    out["cnuc_overlap_pct"]=(100*out.cnuc_union_area_km2/denom).clip(upper=100)
    out["cnuc_protecao_integral_pct"]=(100*out.cnuc_protecao_integral_area_km2/denom).clip(upper=100)
    out["cnuc_uso_sustentavel_pct"]=(100*out.cnuc_uso_sustentavel_area_km2/denom).clip(upper=100)
    out["cnuc_any_overlap"]=out.cnuc_union_area_km2.gt(0)
    out["cnuc_integral_any_overlap"]=out.cnuc_protecao_integral_area_km2.gt(0)
    pct=out["cnuc_overlap_pct"].to_numpy(float)
    out["environment_constraint_tier"]=np.select(
        [pct<=0,pct<1,pct<10,pct<30],
        ["none","trace_<1pct","low_1_10pct","material_10_30pct"],
        default="high_30pct_plus",
    )
    out["environment_hard_screen_flag"]=out.cnuc_integral_any_overlap

    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(args.out,index=False)
    qa={
        "source_shapefile":str(shp),
        "municipalities":int(len(out)),
        "municipalities_any_cnuc_overlap":int(out.cnuc_any_overlap.sum()),
        "municipalities_integral_protection_overlap":int(out.cnuc_integral_any_overlap.sum()),
        "municipalities_overlap_ge_10pct":int((out.cnuc_overlap_pct>=10).sum()),
        "municipalities_overlap_ge_30pct":int((out.cnuc_overlap_pct>=30).sum()),
        "max_overlap_pct":float(out.cnuc_overlap_pct.max()),
        "interpretation":"Municipality screening constraint only; parcel feasibility requires exact site geometry and licensing/legal review.",
    }
    q=Path(args.qa)
    q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(qa,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
