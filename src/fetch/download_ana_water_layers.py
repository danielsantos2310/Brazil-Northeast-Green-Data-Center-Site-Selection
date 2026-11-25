#!/usr/bin/env python3
"""Download ANA/SNIRH surface-water availability evidence for Northeast Brazil.

Primary layer: official surface-water availability (DISPQ95, m3/s), with geometry.
The output is hydrological evidence only; it is not a water right, utility commitment,
permitted sustainable withdrawal, drought guarantee, or parcel-feasibility result.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests

Q95_URL = "https://portal1.snirh.gov.br/server/rest/services/dados_abertos/Disponibilidade_Hidrica_Superficial/FeatureServer/0/query"
NE_BBOX = (-48.8, -18.5, -34.7, -1.0)
FIELDS = "OBJECTID,NUAREAMONT,DISPQ95,ID,DSVERSAO,NMRIO,DEDOMINIAL"
UA = "Mozilla/5.0 (compatible; Northeast-Green-Data-Centre-Research/1.0)"
RETRYABLE = {429, 500, 502, 503, 504}


def get_page(session: requests.Session, *, offset: int, page_size: int, retries: int = 7) -> dict:
    xmin, ymin, xmax, ymax = NE_BBOX
    params = {
        "where": "1=1",
        "geometry": f"{xmin},{ymin},{xmax},{ymax}",
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4674",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": FIELDS,
        "returnGeometry": "true",
        "outSR": "4674",
        "orderByFields": "OBJECTID ASC",
        "resultOffset": offset,
        "resultRecordCount": page_size,
        "f": "geojson",
    }
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = session.get(Q95_URL, params=params, timeout=180)
            if response.status_code in RETRYABLE:
                raise requests.HTTPError(
                    f"retryable HTTP {response.status_code}", response=response
                )
            response.raise_for_status()
            payload = response.json()
            if "error" in payload:
                raise RuntimeError(f"ANA ArcGIS error: {payload['error']}")
            return payload
        except (requests.RequestException, ValueError, RuntimeError) as exc:
            last_error = exc
            if attempt == retries:
                break
            wait = min(60, 2 ** attempt)
            print(
                f"ANA page retry offset={offset:,} size={page_size} "
                f"attempt={attempt}/{retries} wait={wait}s error={exc}",
                flush=True,
            )
            time.sleep(wait)
    raise RuntimeError(
        f"ANA page failed after {retries} attempts at offset={offset}, "
        f"page_size={page_size}: {last_error}"
    )


def fetch_geojson(default_page_size: int = 500) -> dict:
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    features: list[dict] = []
    offset = 0
    page_size = default_page_size

    while True:
        try:
            payload = get_page(session, offset=offset, page_size=page_size)
        except RuntimeError:
            if page_size > 125:
                page_size //= 2
                print(
                    f"Reducing ANA page size at offset={offset:,} to {page_size}",
                    flush=True,
                )
                continue
            raise

        batch = payload.get("features", [])
        if not batch:
            print(f"offset={offset:,} batch=0 total={len(features):,}", flush=True)
            break

        features.extend(batch)
        print(
            f"offset={offset:,} size={page_size} batch={len(batch):,} "
            f"total={len(features):,}",
            flush=True,
        )

        if len(batch) < page_size:
            break
        offset += len(batch)
        time.sleep(0.20)

    if not features:
        raise RuntimeError("ANA query returned zero features for the Northeast envelope")

    object_ids = [f.get("properties", {}).get("OBJECTID") for f in features]
    nonnull = [x for x in object_ids if x is not None]
    if len(nonnull) != len(set(nonnull)):
        raise RuntimeError("Duplicate OBJECTID values detected across ANA pages")

    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="data/interim/ana_surface_water_availability_ne.geojson",
    )
    parser.add_argument("--page-size", type=int, default=500)
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = fetch_geojson(args.page_size)
    out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"saved {len(data['features']):,} features -> {out}")


if __name__ == "__main__":
    main()
