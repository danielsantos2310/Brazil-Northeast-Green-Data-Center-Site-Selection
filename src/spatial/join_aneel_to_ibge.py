"""Spatially join cleaned ANEEL SIGA plant points to IBGE 2025 municipalities."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd

NE_STATES = {"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"}
TARGET_CRS = "EPSG:4674"  # SIRGAS 2000


def load_ibge(ibge_dir: str | Path) -> gpd.GeoDataFrame:
    root = Path(ibge_dir)
    shp_paths = sorted(root.rglob("*_Municipios_2025.shp"))
    if not shp_paths:
        raise FileNotFoundError(
            f"No *_Municipios_2025.shp files found below {root}. "
            "Run the IBGE fetch script with --extract first."
        )

    frames = []
    for path in shp_paths:
        gdf = gpd.read_file(path)
        frames.append(gdf)

    ibge = gpd.GeoDataFrame(
        pd.concat(frames, ignore_index=True),
        geometry="geometry",
        crs=frames[0].crs,
    )

    if ibge.crs is None:
        raise ValueError("IBGE geometry has no CRS metadata.")
    ibge = ibge.to_crs(TARGET_CRS)

    # IBGE municipal mesh historically uses SIGLA or SIGLA_UF depending release.
    if "SIGLA_UF" in ibge.columns:
        uf_col = "SIGLA_UF"
    elif "SIGLA" in ibge.columns:
        uf_col = "SIGLA"
    else:
        # Per-state archive names still let us validate through the loaded set,
        # but a state field is required for reliable downstream joins.
        raise ValueError(f"Could not find IBGE state code column in {list(ibge.columns)}")

    required = {"CD_MUN", "NM_MUN", uf_col, "geometry"}
    missing = required.difference(ibge.columns)
    if missing:
        raise ValueError(f"Missing IBGE columns: {sorted(missing)}")

    ibge = ibge.loc[ibge[uf_col].isin(NE_STATES)].copy()
    ibge = ibge.rename(columns={uf_col: "state"})
    ibge["ibge_code"] = ibge["CD_MUN"].astype("string")
    ibge["municipality"] = ibge["NM_MUN"].astype("string")

    if ibge["ibge_code"].duplicated().any():
        dupes = ibge.loc[ibge["ibge_code"].duplicated(), "ibge_code"].tolist()
        raise ValueError(f"Duplicate IBGE municipality codes: {dupes[:10]}")

    return ibge[["ibge_code", "municipality", "state", "geometry"]]


def load_aneel_points(path: str | Path) -> gpd.GeoDataFrame:
    df = pd.read_parquet(path)
    required = {
        "CodCEG",
        "SigUFPrincipal",
        "technology",
        "DscFaseUsina",
        "capacity_granted_mw",
        "capacity_fiscalized_mw",
        "latitude",
        "longitude",
        "coordinate_valid",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing cleaned ANEEL columns: {sorted(missing)}")

    valid = df.loc[df["coordinate_valid"]].copy()
    points = gpd.GeoDataFrame(
        valid,
        geometry=gpd.points_from_xy(valid["longitude"], valid["latitude"]),
        crs="EPSG:4326",
    )
    return points.to_crs(TARGET_CRS)


def build_municipality_summary(joined: gpd.GeoDataFrame) -> pd.DataFrame:
    operating = joined["DscFaseUsina"].eq("Operação")
    wind = joined["technology"].eq("Wind")
    solar = joined["technology"].eq("Solar")
    wind_solar = wind | solar
    pipeline = ~operating

    base = (
        joined[["ibge_code", "municipality", "state"]]
        .drop_duplicates()
        .set_index("ibge_code")
    )

    def summed(mask: pd.Series, column: str, name: str) -> pd.Series:
        return (
            joined.loc[mask]
            .groupby("ibge_code")[column]
            .sum(min_count=1)
            .rename(name)
        )

    metrics = [
        summed(operating & wind, "capacity_fiscalized_mw", "operating_wind_mw"),
        summed(operating & solar, "capacity_fiscalized_mw", "operating_solar_mw"),
        summed(
            operating & wind_solar,
            "capacity_fiscalized_mw",
            "operating_wind_solar_mw",
        ),
        summed(
            pipeline & wind_solar,
            "capacity_granted_mw",
            "wind_solar_pipeline_granted_mw",
        ),
    ]

    out = base.join(metrics).fillna(0).reset_index()
    count = (
        joined.loc[operating & wind_solar]
        .groupby("ibge_code")["CodCEG"]
        .size()
        .rename("operating_wind_solar_plants")
    )
    out = out.set_index("ibge_code").join(count).fillna(
        {"operating_wind_solar_plants": 0}
    )
    out["operating_wind_solar_plants"] = out[
        "operating_wind_solar_plants"
    ].astype(int)
    return out.reset_index().sort_values(
        "operating_wind_solar_mw", ascending=False
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--aneel-parquet",
        default="data/processed/aneel_siga_northeast_clean.parquet",
    )
    parser.add_argument("--ibge-dir", default="data/raw/ibge")
    parser.add_argument("--output-dir", default="data/processed")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    ibge = load_ibge(args.ibge_dir)
    points = load_aneel_points(args.aneel_parquet)

    joined = gpd.sjoin(
        points,
        ibge,
        how="left",
        predicate="within",
    )

    unmatched = joined["ibge_code"].isna()
    print(f"Valid ANEEL point records: {len(joined):,}")
    print(f"Unmatched to IBGE municipality: {unmatched.sum():,}")

    joined.drop(columns=["index_right"], errors="ignore").to_parquet(
        output / "aneel_ibge_plant_join.parquet",
        index=False,
    )

    summary = build_municipality_summary(joined.loc[~unmatched].copy())
    summary.to_csv(
        output / "aneel_ibge_municipality_energy_summary.csv",
        index=False,
    )


if __name__ == "__main__":
    main()
