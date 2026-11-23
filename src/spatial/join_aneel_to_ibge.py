"""Spatially join cleaned ANEEL SIGA plant points to IBGE 2025 municipalities.

Step 04 keeps the complete Northeast municipality universe. Municipalities with
no ANEEL generation records remain in the output with zero generation metrics.

Cross-state coordinate assignments are accepted only when the joined IBGE
municipality is explicitly named in ANEEL's municipality field. Other
cross-state matches remain visible for QA but are excluded from municipality
aggregates.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import geopandas as gpd
import pandas as pd

NE_STATES = {"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"}
TARGET_CRS = "EPSG:4674"  # SIRGAS 2000


def _normalise_text(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def load_ibge(ibge_dir: str | Path) -> gpd.GeoDataFrame:
    root = Path(ibge_dir)
    shp_paths = sorted(root.rglob("*_Municipios_2025.shp"))
    if not shp_paths:
        raise FileNotFoundError(
            f"No *_Municipios_2025.shp files found below {root}. "
            "Run the IBGE fetch script with --extract first."
        )

    frames = [gpd.read_file(path) for path in shp_paths]
    ibge = gpd.GeoDataFrame(
        pd.concat(frames, ignore_index=True),
        geometry="geometry",
        crs=frames[0].crs,
    )

    if ibge.crs is None:
        raise ValueError("IBGE geometry has no CRS metadata.")
    ibge = ibge.to_crs(TARGET_CRS)

    if "SIGLA_UF" in ibge.columns:
        uf_col = "SIGLA_UF"
    elif "SIGLA" in ibge.columns:
        uf_col = "SIGLA"
    else:
        raise ValueError(
            f"Could not find IBGE state code column in {list(ibge.columns)}"
        )

    required = {"CD_MUN", "NM_MUN", uf_col, "geometry"}
    missing = required.difference(ibge.columns)
    if missing:
        raise ValueError(f"Missing IBGE columns: {sorted(missing)}")

    ibge = ibge.loc[ibge[uf_col].isin(NE_STATES)].copy()
    ibge = ibge.rename(columns={uf_col: "state"})
    ibge["ibge_code"] = ibge["CD_MUN"].astype("string")
    ibge["municipality"] = ibge["NM_MUN"].astype("string")

    if ibge["ibge_code"].duplicated().any():
        dupes = ibge.loc[
            ibge["ibge_code"].duplicated(), "ibge_code"
        ].tolist()
        raise ValueError(f"Duplicate IBGE municipality codes: {dupes[:10]}")
    if not ibge.geometry.notna().all():
        raise ValueError("IBGE municipality geometry contains null values.")
    if not ibge.geometry.is_valid.all():
        raise ValueError("IBGE municipality geometry contains invalid polygons.")

    keep = ["ibge_code", "municipality", "state"]
    if "AREA_KM2" in ibge.columns:
        keep.append("AREA_KM2")
    keep.append("geometry")
    return ibge[keep].copy()


def load_aneel_points(path: str | Path) -> gpd.GeoDataFrame:
    df = pd.read_parquet(path)
    required = {
        "CodCEG",
        "SigUFPrincipal",
        "DscMuninicpios",
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
        geometry=gpd.points_from_xy(
            valid["longitude"],
            valid["latitude"],
        ),
        crs="EPSG:4326",
    )
    return points.to_crs(TARGET_CRS)


def classify_assignments(joined: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    out = joined.copy()
    matched = out["ibge_code"].notna()
    out["state_matches_aneel"] = (
        matched & out["state"].eq(out["SigUFPrincipal"])
    )
    out["cross_state_declared_municipality"] = False

    cross_state = matched & ~out["state_matches_aneel"]
    for idx in out.index[cross_state]:
        municipality = _normalise_text(out.at[idx, "municipality"])
        declared = _normalise_text(out.at[idx, "DscMuninicpios"])
        out.at[idx, "cross_state_declared_municipality"] = (
            bool(municipality) and municipality in declared
        )

    out["municipality_assignment_accepted"] = matched & (
        out["state_matches_aneel"]
        | out["cross_state_declared_municipality"]
    )
    out["municipality_assignment_quality"] = "unmatched"
    out.loc[
        out["state_matches_aneel"],
        "municipality_assignment_quality",
    ] = "state_match"
    out.loc[
        out["cross_state_declared_municipality"],
        "municipality_assignment_quality",
    ] = "cross_state_declared_municipality"
    out.loc[
        matched & ~out["municipality_assignment_accepted"],
        "municipality_assignment_quality",
    ] = "state_mismatch_suspect"
    return out


def build_municipality_summary(
    joined: gpd.GeoDataFrame,
    ibge: gpd.GeoDataFrame,
) -> pd.DataFrame:
    base_cols = ["ibge_code", "municipality", "state"]
    if "AREA_KM2" in ibge.columns:
        base_cols.append("AREA_KM2")
    base = (
        ibge[base_cols]
        .drop_duplicates("ibge_code")
        .set_index("ibge_code")
    )

    accepted = joined.loc[
        joined["municipality_assignment_accepted"]
    ].copy()
    operating = accepted["DscFaseUsina"].eq("Operação")
    wind = accepted["technology"].eq("Wind")
    solar = accepted["technology"].eq("Solar")
    wind_solar = wind | solar
    pipeline = ~operating

    def summed(mask: pd.Series, column: str, name: str) -> pd.Series:
        return (
            accepted.loc[mask]
            .groupby("ibge_code")[column]
            .sum(min_count=1)
            .rename(name)
        )

    metrics = [
        summed(
            operating & wind,
            "capacity_fiscalized_mw",
            "operating_wind_mw",
        ),
        summed(
            operating & solar,
            "capacity_fiscalized_mw",
            "operating_solar_mw",
        ),
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

    out = base.copy()
    for metric in metrics:
        out = out.join(metric)

    count = (
        accepted.loc[operating & wind_solar]
        .groupby("ibge_code")["CodCEG"]
        .size()
        .rename("operating_wind_solar_plants")
    )
    out = out.join(count).fillna(0).reset_index()
    out["operating_wind_solar_plants"] = out[
        "operating_wind_solar_plants"
    ].astype(int)

    return out.sort_values(
        ["operating_wind_solar_mw", "wind_solar_pipeline_granted_mw"],
        ascending=False,
    )


def build_qa(
    joined: gpd.GeoDataFrame,
    ibge: gpd.GeoDataFrame,
    summary: pd.DataFrame,
) -> pd.DataFrame:
    matched = joined["ibge_code"].notna()
    return pd.DataFrame(
        [
            {
                "metric": "ibge_municipalities_northeast",
                "value": len(ibge),
                "interpretation": "Complete candidate municipality universe",
            },
            {
                "metric": "aneel_valid_coordinate_points",
                "value": len(joined),
                "interpretation": "ANEEL records entering point-in-polygon join",
            },
            {
                "metric": "spatial_join_matched",
                "value": int(matched.sum()),
                "interpretation": "Points inside an IBGE municipality polygon",
            },
            {
                "metric": "spatial_join_unmatched",
                "value": int((~matched).sum()),
                "interpretation": "Review required; never silently snapped",
            },
            {
                "metric": "matched_state_consistent",
                "value": int(joined["state_matches_aneel"].sum()),
                "interpretation": "IBGE polygon state equals ANEEL principal state",
            },
            {
                "metric": "matched_cross_state_declared",
                "value": int(
                    joined["cross_state_declared_municipality"].sum()
                ),
                "interpretation": (
                    "Cross-state polygon match explicitly supported by "
                    "ANEEL municipality text"
                ),
            },
            {
                "metric": "spatial_assignment_suspect_excluded",
                "value": int(
                    joined["municipality_assignment_quality"]
                    .eq("state_mismatch_suspect")
                    .sum()
                ),
                "interpretation": (
                    "Cross-state matches without textual support; excluded "
                    "from municipality aggregates"
                ),
            },
            {
                "metric": "spatial_assignment_accepted",
                "value": int(
                    joined["municipality_assignment_accepted"].sum()
                ),
                "interpretation": "Assignments used in municipality aggregates",
            },
            {
                "metric": "municipality_summary_rows",
                "value": len(summary),
                "interpretation": "Must equal complete IBGE candidate universe",
            },
            {
                "metric": "municipalities_zero_operating_wind_solar",
                "value": int(
                    summary["operating_wind_solar_mw"].eq(0).sum()
                ),
                "interpretation": (
                    "Retained as valid candidates rather than dropped"
                ),
            },
        ]
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

    # Canonical municipality layer consumed by Step 05 grid metrics.
    ibge.to_parquet(
        output / "ibge_northeast_municipalities.parquet",
        index=False,
    )

    joined = gpd.sjoin(
        points,
        ibge,
        how="left",
        predicate="within",
    ).drop(columns=["index_right"], errors="ignore")
    joined = classify_assignments(joined)

    joined.to_parquet(
        output / "aneel_ibge_plant_join.parquet",
        index=False,
    )

    summary = build_municipality_summary(joined, ibge)
    summary.to_csv(
        output / "aneel_ibge_municipality_energy_summary.csv",
        index=False,
    )

    qa = build_qa(joined, ibge, summary)
    qa.to_csv(output / "ibge_spatial_join_qa.csv", index=False)

    issues = joined.loc[
        joined["municipality_assignment_quality"].isin(
            ["unmatched", "state_mismatch_suspect"]
        )
    ].drop(columns="geometry", errors="ignore")
    issues.to_csv(
        output / "aneel_ibge_assignment_issues.csv",
        index=False,
    )

    print(f"IBGE Northeast municipalities: {len(ibge):,}")
    print(f"Valid ANEEL point records: {len(joined):,}")
    print(
        "Accepted municipality assignments: "
        f"{joined['municipality_assignment_accepted'].sum():,}"
    )
    print(
        "QA issues: "
        f"{len(issues):,} "
        "(unmatched or unsupported cross-state assignment)"
    )
    print(f"Municipality summary rows: {len(summary):,}")


if __name__ == "__main__":
    main()
