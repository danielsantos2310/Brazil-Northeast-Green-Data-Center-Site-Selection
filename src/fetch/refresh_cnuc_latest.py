#!/usr/bin/env python3
"""Resolve and download the latest versioned CNUC CSV/SHP resources from MMA CKAN."""
from __future__ import annotations
import argparse, json, re, zipfile
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import requests

PACKAGE_ID="44b6dc8a-dc82-4a84-8d95-1b0da7c85dac"
API=f"https://dados.mma.gov.br/api/3/action/package_show?id={PACKAGE_ID}"
UA="Mozilla/5.0 (compatible; Northeast-Green-Data-Centre-Research/1.0)"

def add_download_flag(url:str)->str:
    p=urlparse(url); q=dict(parse_qsl(p.query,keep_blank_values=True)); q["download"]="1"
    return urlunparse((p.scheme,p.netloc,p.path,p.params,urlencode(q),p.fragment))

def version(r):
    text=(r.get("name") or "")+" "+(r.get("description") or "")
    m=re.search(r"(20\d{2})[_-](\d{2})",text)
    return tuple(map(int,m.groups())) if m else (0,0)

def download(url:str,dest:Path,expect_zip=False)->dict:
    s=requests.Session(); s.headers.update({"User-Agent":UA})
    attempts=[url]
    if "sharepoint.com" in url.lower(): attempts.append(add_download_flag(url))
    last=None
    for candidate in attempts:
        r=s.get(candidate,timeout=240,allow_redirects=True); last=r
        if r.status_code>=400: continue
        content=r.content
        if expect_zip and not content.startswith(b"PK"): continue
        dest.write_bytes(content)
        return {"requested_url":candidate,"final_url":r.url,"status":r.status_code,
                "content_type":r.headers.get("content-type"),"bytes":len(content)}
    if last is not None:
        last.raise_for_status()
        raise RuntimeError(f"Expected ZIP but received {last.headers.get('content-type')} from {last.url}")
    raise RuntimeError(f"Download failed: {url}")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--outdir",default="cnuc_latest"); args=ap.parse_args()
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    meta=requests.get(API,headers={"User-Agent":UA},timeout=60); meta.raise_for_status()
    pkg=meta.json()["result"]; resources=pkg["resources"]
    csvs=[r for r in resources if (r.get("format") or "").lower()=="csv" and version(r)>(0,0)]
    shps=[r for r in resources if ("shp" in (r.get("format") or "").lower() or "zip" in (r.get("format") or "").lower()) and version(r)>(0,0)]
    selected=[]
    if csvs: selected.append(max(csvs,key=version))
    if shps: selected.append(max(shps,key=version))
    if not selected: raise RuntimeError("No versioned CNUC resources found")
    (out/"ckan_package_metadata.json").write_text(json.dumps(pkg,indent=2,ensure_ascii=False),encoding="utf-8")
    manifest={"package_id":PACKAGE_ID,"package_modified":pkg.get("metadata_modified"),"selected":[]}
    for r in selected:
        url=r["url"]; fmt=(r.get("format") or "").lower(); name=r.get("name") or r["id"]
        is_zip=("zip" in fmt or "shp" in fmt); suffix=".zip" if is_zip else ".csv"
        safe=re.sub(r"[^A-Za-z0-9_.-]+","_",name).strip("_"); dest=out/(safe+suffix)
        dl=download(url,dest,expect_zip=is_zip)
        rec={k:r.get(k) for k in ["id","name","format","url","created","last_modified","description"]}
        rec["version"]=version(r); rec["download"]=dl; rec["local_file"]=str(dest); manifest["selected"].append(rec)
        if is_zip:
            with zipfile.ZipFile(dest) as z:
                members=z.namelist()
                if not any(x.lower().endswith(".shp") for x in members): raise RuntimeError(f"ZIP has no .shp: {dest}")
                z.extractall(out/"shapefile")
    (out/"selected_resources.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
