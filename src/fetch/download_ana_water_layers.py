#!/usr/bin/env python3
"""Download ANA/SNIRH surface-water availability evidence for Northeast Brazil.

Primary layer: official surface-water availability (DISPQ95, m3/s), with geometry.
The output is hydrological evidence only; it is not a water right, utility commitment,
permitted sustainable withdrawal, drought guarantee, or parcel-feasibility result.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
import requests

Q95_URL="https://portal1.snirh.gov.br/server/rest/services/dados_abertos/Disponibilidade_Hidrica_Superficial/FeatureServer/0/query"
NE_BBOX=(-48.8,-18.5,-34.7,-1.0)
FIELDS="OBJECTID,NUAREAMONT,DISPQ95,ID,DSVERSAO,NMRIO,DEDOMINIAL"
UA="Mozilla/5.0 (compatible; Northeast-Green-Data-Centre-Research/1.0)"

def fetch_geojson(url:str,bbox,page_size=1000,pause=0.15):
    session=requests.Session(); session.headers.update({"User-Agent":UA})
    features=[]; offset=0; xmin,ymin,xmax,ymax=bbox
    while True:
        params={"where":"1=1","geometry":f"{xmin},{ymin},{xmax},{ymax}",
          "geometryType":"esriGeometryEnvelope","inSR":"4674",
          "spatialRel":"esriSpatialRelIntersects","outFields":FIELDS,
          "returnGeometry":"true","outSR":"4674","orderByFields":"OBJECTID ASC",
          "resultOffset":offset,"resultRecordCount":page_size,"f":"geojson"}
        r=session.get(url,params=params,timeout=180); r.raise_for_status()
        payload=r.json()
        if "error" in payload: raise RuntimeError(f"ANA ArcGIS error: {payload['error']}")
        batch=payload.get("features",[])
        features.extend(batch)
        print(f"offset={offset:,} batch={len(batch):,} total={len(features):,}",flush=True)
        if len(batch)<page_size: break
        offset+=len(batch); time.sleep(pause)
    if not features: raise RuntimeError("ANA query returned zero features for the Northeast envelope")
    return {"type":"FeatureCollection","features":features}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="ana_surface_water_availability_ne.geojson"); args=ap.parse_args()
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    data=fetch_geojson(Q95_URL,NE_BBOX)
    out.write_text(json.dumps(data,ensure_ascii=False),encoding="utf-8")
    print(f"saved {len(data['features']):,} features -> {out}")

if __name__=="__main__": main()
