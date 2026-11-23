from __future__ import annotations

from pathlib import Path
import hashlib
import json
import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "aneel_siga_empreendimentos_geracao.csv": {
        "url": "https://dadosabertos.aneel.gov.br/dataset/6d90b77c-c5f5-4d81-bdec-7bc619494bb9/resource/11ec447d-698d-4ab8-977f-b424d5deee6a/download/siga-empreendimentos-geracao.csv",
        "type": "file",
    },
    "ons_subestacoes_operacao.csv": {
        "url": "https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/subestacao/SUBESTACAO.csv",
        "type": "file",
    },
    "epe_subestacoes_existentes.geojson": {
        "url": "https://gisepeprd2.epe.gov.br/arcgis/rest/services/SMA/WFS_Webmap_EPE/MapServer/19/query",
        "type": "arcgis",
    },
    "epe_subestacoes_planejadas.geojson": {
        "url": "https://gisepeprd2.epe.gov.br/arcgis/rest/services/SMA/WFS_Webmap_EPE/MapServer/8/query",
        "type": "arcgis",
    },
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def download_file(url: str, path: Path) -> None:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    path.write_bytes(r.content)

def download_arcgis(url: str, path: Path) -> None:
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "4674",
    }
    r = requests.get(url, params=params, timeout=120)
    r.raise_for_status()
    payload = r.json()
    if "features" not in payload:
        raise RuntimeError(f"Unexpected ArcGIS response from {url}: {payload}")
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

def main() -> None:
    manifest = []

    for filename, meta in SOURCES.items():
        path = RAW_DIR / filename
        print(f"Downloading {filename}...")

        if meta["type"] == "arcgis":
            download_arcgis(meta["url"], path)
        else:
            download_file(meta["url"], path)

        manifest.append({
            "filename": filename,
            "source_url": meta["url"],
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    manifest_path = RAW_DIR / "download_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Done. Manifest: {manifest_path}")

if __name__ == "__main__":
    main()
