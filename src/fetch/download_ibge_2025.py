"""Download the official IBGE 2025 municipal meshes for Northeast Brazil.

Source directory:
https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/
malhas_municipais/municipio_2025/UFs/

The raw ZIP archives should also be preserved in the project's private
Google Drive raw-data workspace. This script is for reproducible local fetches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import requests

NE_STATES = ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]
BASE_URL = (
    "https://geoftp.ibge.gov.br/organizacao_do_territorio/"
    "malhas_territoriais/malhas_municipais/municipio_2025/UFs"
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, path: Path) -> None:
    with requests.get(url, timeout=180, stream=True) as response:
        response.raise_for_status()
        with path.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/raw/ibge")
    parser.add_argument("--extract", action="store_true")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []

    for uf in NE_STATES:
        filename = f"{uf}_Municipios_2025.zip"
        url = f"{BASE_URL}/{uf}/{filename}"
        path = out / filename

        if not path.exists():
            print(f"Downloading {uf}: {url}")
            download(url, path)
        else:
            print(f"Using existing {path}")

        item = {
            "state": uf,
            "filename": filename,
            "source_url": url,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        manifest.append(item)

        if args.extract:
            extract_dir = out / uf
            extract_dir.mkdir(exist_ok=True)
            with zipfile.ZipFile(path) as zf:
                zf.extractall(extract_dir)

    (out / "ibge_2025_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {out / 'ibge_2025_manifest.json'}")


if __name__ == "__main__":
    main()
