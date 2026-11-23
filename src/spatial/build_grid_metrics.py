"""Build municipality-level grid-proximity indicators from EPE infrastructure.

This is a screening layer. Physical proximity to a substation or transmission
line is not evidence of spare connection capacity.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd

TARGET_CRS = "EPSG:4674"  # SIRGAS 2000
# Region-wide screening CRS centered on Northeast Brazil. One-per-state QA on
# 2026-11-23 showed <0.55% error versus geodesic nearest-substation distance.
DISTANCE_CRS = (
    "+proj=lcc +lat_1=-3 +lat_2=-15 +lat_0=-9 +lon_0=-40 "
    "+ellps=GRS80 +units=m +no_defs"
)
MIN_HIGH_VOLTAGE_KV = 230.0


def _read(path: str | Path) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(TARGET_CRS)
    return gdf.to_crs(TARGET_CRS)


def _max_voltage_numeric(series: pd.Series) -> pd.Series:
    """Parse maximum voltage from values such as '525/230' or 500."""
    def parse(value: object) -> float | None:
        values = re.findall(r"\d+(?:[.,]\d+)?", str(value))
        if not values:
            return None
        return max(float(item.replace(",", ".")) for item in values)

    return series.map(parse).astype("Float64")


def _normalise_voltage(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    out = gdf.copy()
    if "Tensao" not in out.columns:
        raise ValueError(f"EPE layer has no Tensao field: {list(out.columns)}")
    out["voltage_kv"] = _max_voltage_numeric(out["Tensao"])
    return out


def _northeast_substations(
    substations: gpd.GeoDataFrame,
    municipalities: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    joined = gpd.sjoin(
        substations,
        municipalities[["ibge_code", "municipality", "state", "geometry"]],
        how="inner",
        predicate="intersects",
    )
    joined = joined.loc[~joined.index.duplicated(keep="first")]
    return gpd.GeoDataFrame(
        joined.drop(columns="index_right", errors="ignore"),
        geometry="geometry",
        crs=TARGET_CRS,
    )


def _northeast_lines(
    lines: gpd.GeoDataFrame,
    municipalities: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    region = municipalities.geometry.union_all()
    return lines.loc[lines.geometry.intersects(region)].copy()


def _nearest(
    origins_projected: gpd.GeoDataFrame,
    targets: gpd.GeoDataFrame,
    prefix: str,
) -> pd.DataFrame:
    targets = targets.loc[
        targets["voltage_kv"].ge(MIN_HIGH_VOLTAGE_KV)
    ].copy()
    if targets.empty:
        raise ValueError(f"No >=230 kV EPE targets available for {prefix}")

    targets = targets.to_crs(DISTANCE_CRS)
    keep = ["geometry"]
    rename: dict[str, str] = {}
    for column in ["Nome", "voltage_kv", "Ano_Opera", "Ano_Planej", "OBJECTID"]:
        if column in targets.columns:
            keep.append(column)
            rename[column] = f"{prefix}_{column.lower()}"

    targets = targets[keep].rename(columns=rename)
    joined = gpd.sjoin_nearest(
        origins_projected[["ibge_code", "geometry"]],
        targets,
        how="left",
        distance_col="_distance_m",
    )
    joined = (
        joined.sort_values(["ibge_code", "_distance_m"])
        .drop_duplicates("ibge_code")
    )

    result = pd.DataFrame(
        {
            "ibge_code": joined["ibge_code"].astype("string"),
            f"{prefix}_distance_km": joined["_distance_m"] / 1000,
        }
    )
    for column in rename.values():
        if column in joined.columns:
            result[column] = joined[column].values
    return result


def _substation_counts(
    origins_projected: gpd.GeoDataFrame,
    substations: gpd.GeoDataFrame,
    label: str,
) -> pd.DataFrame:
    substations = substations.loc[
        substations["voltage_kv"].ge(MIN_HIGH_VOLTAGE_KV)
    ].to_crs(DISTANCE_CRS)

    result = pd.DataFrame(
        {"ibge_code": origins_projected["ibge_code"].astype("string")}
    )
    for radius_km in (25, 50):
        buffers = origins_projected[["ibge_code", "geometry"]].copy()
        buffers["geometry"] = buffers.geometry.buffer(radius_km * 1000)
        joined = gpd.sjoin(
            substations[["geometry"]],
            buffers,
            how="inner",
            predicate="within",
        )
        counts = joined.groupby("ibge_code").size()
        result[f"{label}_within_{radius_km}km"] = (
            result["ibge_code"].map(counts).fillna(0).astype(int)
        )
    return result


def _line_intersection_flag(
    municipalities: gpd.GeoDataFrame,
    lines: gpd.GeoDataFrame,
    column_name: str,
) -> pd.DataFrame:
    lines = lines.loc[lines["voltage_kv"].ge(MIN_HIGH_VOLTAGE_KV)]
    joined = gpd.sjoin(
        municipalities[["ibge_code", "geometry"]],
        lines[["geometry"]],
        how="left",
        predicate="intersects",
    )
    flags = (
        joined.groupby("ibge_code")["index_right"]
        .apply(lambda values: values.notna().any())
    )
    return pd.DataFrame(
        {
            "ibge_code": municipalities["ibge_code"].astype("string"),
            column_name: municipalities["ibge_code"].map(flags).fillna(False),
        }
    )


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
    parser.add_argument(
        "--existing-lines",
        default="data/raw/epe/epe_linhas_de_transmissao_base_existente.geojson",
    )
    parser.add_argument(
        "--planned-lines",
        default="data/raw/epe/epe_linhas_de_transmissao_expansao_planejada.geojson",
    )
    parser.add_argument("--output-dir", default="data/processed")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    municipalities = gpd.read_parquet(args.municipalities).to_crs(TARGET_CRS)
    if municipalities["ibge_code"].duplicated().any():
        raise ValueError("Duplicate IBGE municipality codes in candidate layer.")

    existing_substations = _normalise_voltage(_read(args.existing_substations))
    planned_substations = _normalise_voltage(_read(args.planned_substations))
    existing_lines = _normalise_voltage(_read(args.existing_lines))
    planned_lines = _normalise_voltage(_read(args.planned_lines))

    for name, frame in {
        "existing substations": existing_substations,
        "planned substations": planned_substations,
        "existing lines": existing_lines,
        "planned lines": planned_lines,
    }.items():
        if frame.geometry.isna().any():
            raise ValueError(f"EPE {name} contains null geometry.")

    existing_substations_ne = _northeast_substations(
        existing_substations, municipalities
    )
    planned_substations_ne = _northeast_substations(
        planned_substations, municipalities
    )
    existing_lines_ne = _northeast_lines(existing_lines, municipalities)
    planned_lines_ne = _northeast_lines(planned_lines, municipalities)

    existing_substations_ne.to_file(
        output / "epe_northeast_substations_existing.gpkg",
        driver="GPKG",
    )
    planned_substations_ne.to_file(
        output / "epe_northeast_substations_planned.gpkg",
        driver="GPKG",
    )
    existing_lines_ne.to_file(
        output / "epe_northeast_lines_existing.gpkg",
        driver="GPKG",
    )
    planned_lines_ne.to_file(
        output / "epe_northeast_lines_planned.gpkg",
        driver="GPKG",
    )

    origins = municipalities[
        ["ibge_code", "municipality", "state", "geometry"]
    ].copy()
    origins["geometry"] = origins.geometry.representative_point()
    origins_projected = origins.to_crs(DISTANCE_CRS)

    result = origins[["ibge_code", "municipality", "state"]].copy()
    result["ibge_code"] = result["ibge_code"].astype("string")

    for targets, prefix in (
        (existing_substations, "nearest_existing_substation"),
        (planned_substations, "nearest_planned_substation"),
        (existing_lines, "nearest_existing_transmission_line"),
        (planned_lines, "nearest_planned_transmission_line"),
    ):
        result = result.merge(
            _nearest(origins_projected, targets, prefix),
            on="ibge_code",
            how="left",
        )

    for targets, label in (
        (existing_substations, "existing_substations"),
        (planned_substations, "planned_substations"),
    ):
        result = result.merge(
            _substation_counts(origins_projected, targets, label),
            on="ibge_code",
            how="left",
        )

    for targets, column_name in (
        (
            existing_lines,
            "existing_230kv_line_intersects_municipality",
        ),
        (
            planned_lines,
            "planned_230kv_line_intersects_municipality",
        ),
    ):
        result = result.merge(
            _line_intersection_flag(
                municipalities, targets, column_name
            ),
            on="ibge_code",
            how="left",
        )

    if len(result) != len(municipalities):
        raise ValueError(
            f"Grid output has {len(result)} rows; expected {len(municipalities)}"
        )

    result.to_csv(
        output / "epe_municipality_grid_proximity.csv",
        index=False,
    )

    qa = pd.DataFrame(
        [
            ("ibge_candidate_municipalities", len(municipalities)),
            ("epe_existing_substations_national", len(existing_substations)),
            ("epe_planned_substations_national", len(planned_substations)),
            ("epe_existing_lines_national", len(existing_lines)),
            ("epe_planned_lines_national", len(planned_lines)),
            (
                "epe_existing_substations_northeast",
                len(existing_substations_ne),
            ),
            (
                "epe_planned_substations_northeast",
                len(planned_substations_ne),
            ),
            (
                "epe_existing_lines_intersect_northeast",
                len(existing_lines_ne),
            ),
            (
                "epe_planned_lines_intersect_northeast",
                len(planned_lines_ne),
            ),
            (
                "municipalities_with_existing_substation_within_25km",
                int((result["existing_substations_within_25km"] > 0).sum()),
            ),
            (
                "municipalities_with_existing_substation_within_50km",
                int((result["existing_substations_within_50km"] > 0).sum()),
            ),
            (
                "municipalities_intersected_by_existing_230kv_line",
                int(
                    result[
                        "existing_230kv_line_intersects_municipality"
                    ].sum()
                ),
            ),
            (
                "municipalities_intersected_by_planned_230kv_line",
                int(
                    result[
                        "planned_230kv_line_intersects_municipality"
                    ].sum()
                ),
            ),
        ],
        columns=["metric", "value"],
    )
    qa.to_csv(output / "epe_grid_qa.csv", index=False)

    print(f"Municipality grid rows: {len(result):,}")
    print(f"Northeast existing substations: {len(existing_substations_ne):,}")
    print(f"Northeast planned substations: {len(planned_substations_ne):,}")
    print(f"Northeast-intersecting existing lines: {len(existing_lines_ne):,}")
    print(f"Northeast-intersecting planned lines: {len(planned_lines_ne):,}")
    print(
        "WARNING: proximity to a substation or transmission line is not "
        "evidence of spare grid connection capacity. Connection feasibility "
        "requires ONS/EPE planning evidence and utility/operator due diligence."
    )


if __name__ == "__main__":
    main()
