#!/usr/bin/env python3
"""Combine extracted official IBGE 2025 Northeast municipal shapefiles."""
from __future__ import annotations
import argparse
from pathlib import Path
import geopandas as gpd
import pandas as pd

NE_STATES = ["AL","BA","CE","MA","PB","PE","PI","RN","SE"]

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir", default="data/raw/ibge")
    p.add_argument("--output", default="data/interim/ibge_ne_municipalities_2025.gpkg")
    args=p.parse_args()
    root=Path(args.input_dir); frames=[]
    for uf in NE_STATES:
        candidates=sorted((root/uf).glob("*.shp"))
        if not candidates:
            raise FileNotFoundError(f"No shapefile found for {uf} under {root/uf}")
        g=gpd.read_file(candidates[0])
        if g.crs is None: raise RuntimeError(f"Missing CRS for {candidates[0]}")
        g=g.to_crs(4674)
        required={"CD_MUN","NM_MUN","SIGLA_UF","AREA_KM2","geometry"}
        missing=required-set(g.columns)
        if missing: raise RuntimeError(f"{uf} missing fields: {sorted(missing)}")
        frames.append(g[["CD_MUN","NM_MUN","SIGLA_UF","AREA_KM2","geometry"]])
    out=gpd.GeoDataFrame(pd.concat(frames,ignore_index=True),crs="EPSG:4674")
    out["CD_MUN"]=out["CD_MUN"].astype(str)
    if len(out)!=1794 or out["CD_MUN"].nunique()!=1794:
        raise RuntimeError(f"Unexpected municipality count: rows={len(out)} unique={out.CD_MUN.nunique()}")
    dest=Path(args.output); dest.parent.mkdir(parents=True,exist_ok=True)
    out.to_file(dest,driver="GPKG",layer="municipalities")
    print(f"wrote {len(out)} municipalities -> {dest}")

if __name__=="__main__":
    main()
