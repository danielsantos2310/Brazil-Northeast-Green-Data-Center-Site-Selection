"""Resolve and download ONS open-data resources through its CKAN API.

Avoids hard-coding monthly resource URLs, which can change when ONS republishes
files. Raw downloads should also be archived in the private Google Drive
01_Raw_Data/ONS folder.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import requests

CKAN_API = "https://dados.ons.org.br/api/3/action/package_show"

DATASETS = {
    "substations": "subestacao",
    "wind_curtailment": "restricao_coff_eolica_usi",
    "solar_curtailment": "restricao_coff_fotovoltaica",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def package_show(dataset_id: str) -> dict:
    r = requests.get(CKAN_API, params={"id": dataset_id}, timeout=120)
    r.raise_for_status()
    payload = r.json()
    if not payload.get("success"):
        raise RuntimeError(payload)
    return payload["result"]


def csv_resources(package: dict) -> list[dict]:
    out = []
    for resource in package.get("resources", []):
        fmt = (resource.get("format") or "").upper()
        name = resource.get("name") or ""
        url = resource.get("url") or ""
        if fmt == "CSV" and url:
            out.append(resource)
    return out


def month_from_name(name: str) -> str | None:
    m = re.search(r"(20\d{2})[-_](0[1-9]|1[0-2])", name)
    return f"{m.group(1)}-{m.group(2)}" if m else None


def select_months(resources: list[dict], months: set[str]) -> list[dict]:
    selected = []
    for r in resources:
        month = month_from_name(r.get("name") or "")
        if month in months:
            selected.append(r)
    return selected


def download(url: str, path: Path) -> None:
    with requests.get(url, timeout=180, stream=True) as response:
        response.raise_for_status()
        with path.open("wb") as fh:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="data/raw/ons")
    parser.add_argument(
        "--months",
        nargs="*",
        default=[],
        help="Curtailment months such as 2026-10 2026-11. "
             "No curtailment files are downloaded unless months are supplied.",
    )
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []

    # Current ONS substation snapshot.
    sub_pkg = package_show(DATASETS["substations"])
    sub_csv = csv_resources(sub_pkg)
    if not sub_csv:
        raise RuntimeError("No CSV resource found for ONS subestacao dataset.")

    # Prefer the plain/current Subestacao CSV rather than dictionaries.
    candidates = [
        r for r in sub_csv
        if "dicion" not in (r.get("name") or "").lower()
    ]
    chosen = candidates[0] if candidates else sub_csv[0]
    filename = "ons_subestacoes_operacao.csv"
    path = out / filename
    download(chosen["url"], path)
    manifest.append(
        {
            "dataset": DATASETS["substations"],
            "resource_name": chosen.get("name"),
            "resource_id": chosen.get("id"),
            "source_url": chosen["url"],
            "filename": filename,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
    )

    months = set(args.months)
    if months:
        for key in ("wind_curtailment", "solar_curtailment"):
            dataset_id = DATASETS[key]
            pkg = package_show(dataset_id)
            resources = select_months(csv_resources(pkg), months)
            found = {month_from_name(r.get("name") or "") for r in resources}
            missing = sorted(months - found)
            if missing:
                raise RuntimeError(
                    f"{dataset_id}: requested CSV months not found: {missing}"
                )

            for resource in sorted(
                resources,
                key=lambda r: month_from_name(r.get("name") or "") or "",
            ):
                month = month_from_name(resource.get("name") or "")
                filename = f"ons_{key}_{month}.csv"
                path = out / filename
                download(resource["url"], path)
                manifest.append(
                    {
                        "dataset": dataset_id,
                        "month": month,
                        "resource_name": resource.get("name"),
                        "resource_id": resource.get("id"),
                        "source_url": resource["url"],
                        "filename": filename,
                        "bytes": path.stat().st_size,
                        "sha256": sha256(path),
                    }
                )

    (out / "ons_download_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
