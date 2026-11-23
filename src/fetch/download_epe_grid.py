"""Download EPE grid-infrastructure layers from the official ArcGIS REST service.

Layer IDs are resolved by name at runtime so the pipeline does not depend on
hard-coded ArcGIS layer numbers.

Important: use the WMS_Webmap_EPE MapServer REST service for feature queries.
As verified on 2026-11-23, the parallel WFS_Webmap_EPE service returns the
expected attributes but null geometry for these layers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests

SERVICE = (
    "https://gisepeprd2.epe.gov.br/arcgis/rest/services/"
    "SMA/WMS_Webmap_EPE/MapServer"
)
LAYER_NAMES = [
    "Subestações - Base Existente",
    "Subestações - Expansão Planejada",
    "Linhas de Transmissão - Base Existente",
    "Linhas de Transmissão - Expansão Planejada",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def get_json(url: str, params: dict | None = None) -> dict:
    r = requests.get(url, params=params, timeout=180)
    r.raise_for_status()
    payload = r.json()
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload


def resolve_layers() -> dict[str, int]:
    meta = get_json(SERVICE, {"f": "json"})
    by_name = {layer["name"]: layer["id"] for layer in meta.get("layers", [])}
    missing = [name for name in LAYER_NAMES if name not in by_name]
    if missing:
        raise RuntimeError(f"EPE layers not found: {missing}")
    return {name: by_name[name] for name in LAYER_NAMES}


def download_geojson(layer_id: int) -> dict:
    url = f"{SERVICE}/{layer_id}/query"
    page_size = 2000
    offset = 0
    features = []
    crs = None

    while True:
        payload = get_json(
            url,
            {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4674",
                "f": "geojson",
                "resultOffset": offset,
                "resultRecordCount": page_size,
            },
        )
        page = payload.get("features", [])
        if crs is None:
            crs = payload.get("crs")

        null_geometry = sum(feature.get("geometry") is None for feature in page)
        if null_geometry:
            raise RuntimeError(
                f"EPE layer {layer_id} returned {null_geometry} features "
                "with null geometry. Refusing to save an unusable spatial layer."
            )

        features.extend(page)
        if len(page) < page_size:
            break
        offset += len(page)

    if not features:
        raise RuntimeError(f"EPE layer {layer_id} returned zero features.")

    return {
        "type": "FeatureCollection",
        "features": features,
        **({"crs": crs} if crs else {}),
    }


def safe_name(name: str) -> str:
    return (
        name.lower()
        .replace("ã", "a")
        .replace("õ", "o")
        .replace("ç", "c")
        .replace("é", "e")
        .replace("í", "i")
        .replace(" - ", "_")
        .replace(" ", "_")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/raw/epe")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    layers = resolve_layers()
    manifest = []

    for name, layer_id in layers.items():
        print(f"Downloading {name} (layer {layer_id})")
        geojson = download_geojson(layer_id)
        path = out / f"epe_{safe_name(name)}.geojson"
        path.write_text(
            json.dumps(geojson, ensure_ascii=False),
            encoding="utf-8",
        )
        manifest.append(
            {
                "layer_name": name,
                "layer_id": layer_id,
                "feature_count": len(geojson["features"]),
                "non_null_geometry_count": sum(
                    feature.get("geometry") is not None
                    for feature in geojson["features"]
                ),
                "source_url": f"{SERVICE}/{layer_id}",
                "filename": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "crs": "EPSG:4674",
            }
        )

    (out / "epe_grid_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
