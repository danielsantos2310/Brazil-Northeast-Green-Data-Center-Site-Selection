"""Build municipality-level grid-proximity indicators from EPE infrastructure."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

DISTANCE_CRS = "EPSG:31984"  # SIRGAS 2000 / UTM 24S; suitable for much of NE Brazil.
# For production, distances spanning the full Northeast should be computed in a
# region-appropriate equal-distance/local projection or geodesically. This
# implementation uses per-feature nearest joins after reprojection and is a
# first-pass screen, not an engineering study.


def _read(path: str | Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4674")
    return gdf.to_crs("EPSG:4674")


def _voltage_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string").str.extract(r"(\d+(?:[.,]\d+)?)", expand=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )


def nearest_distance_km(
    origins: gpd.GeoDataFrame,
    targets: gpd.GeoDataFrame,
    target_prefix: str,
) -> pd.DataFrame:
    # Project each dataset consistently for a screening-distance calculation.
    a = origins.to_crs(DISTANCE_CRS)
    b = targets.to_crs(DISTANCE_CRS)
    joined = gpd.sjoin_nearest(
        a,
        b,
        how="left",
        distance_col=f"{target_prefix}_distance_m",
    )
    cols = ["ibge_code", f"{target_prefix}_distance_m"]
    out = joined[cols].copy()
    out[f"{target_prefix}_distance_km"] = out[f"{target_prefix}_distance_m"] / 1000
    return out.drop(columns=f"{target_prefix}_distance_m")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--municipalities",
        default="data/processed/ibge_northeast_municipalities.parquet",
    )
    parser.add_argument(
        "--existing-substations",
        default="data/raw/epe/epe_subestacoes_base_existente.geojson",
    )
    parser.add_argument(
        "--planned-substations",
        default="data/raw/epe/epe_subestacoes_expansao_planejada.geojson",
    )
    parser.add_argument("--output-dir", default="data/processed")
    args = parser.parse_args()

    muni = gpd.read_parquet(args.municipalities).to_crs("EPSG:4674")
    # Representative points avoid using polygon centroids outside irregular polygons.
    rep = muni[["ibge_code", "municipality", "state", "geometry"]].copy()
    rep["geometry"] = rep.geometry.representative_point()

    existing = _read(args.existing_substations)
    planned = _read(args.planned_substations)

    for frame in (existing, planned):
        if "Tensao" in frame.columns:
            frame["voltage_kv"] = _voltage_numeric(frame["Tensao"])

    result = rep[["ibge_code", "municipality", "state"]].copy()
    result = result.merge(
        nearest_distance_km(rep, existing, "nearest_existing_substation"),
        on="ibge_code",
        how="left",
    )
    result = result.merge(
        nearest_distance_km(rep, planned, "nearest_planned_substation"),
        on="ibge_code",
        how="left",
    )

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    result.to_csv(output / "epe_municipality_grid_proximity.csv", index=False)

    print(
        "WARNING: proximity to a substation is not evidence of spare grid "
        "connection capacity. Connection feasibility requires transmission "
        "planning/ONS/EPE studies and ultimately utility/operator due diligence."
    )


if __name__ == "__main__":
    main()
