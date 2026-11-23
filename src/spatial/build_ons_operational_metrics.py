"""Build ONS operating-grid and curtailment indicators by municipality.

Inputs:
- current ONS operating-substation snapshot;
- monthly wind and solar constrained-off CSVs;
- IBGE municipality geometry from Step 04;
- EPE existing substations from Step 05 as an exact-name geocoding fallback.

Curtailment is operational evidence only. It is not free electricity and does
not establish data-centre connection capacity.
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

NE_STATES = {"AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"}
TARGET_CRS = "EPSG:4674"
DISTANCE_CRS = (
    "+proj=lcc +lat_1=-3 +lat_2=-15 +lat_0=-9 +lon_0=-40 "
    "+ellps=GRS80 +units=m +no_defs"
)


def read_ons_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";", encoding="utf-8-sig")


def clean_station_name(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode().upper()
    text = re.sub(r"\bSE\b", " ", text)
    text = re.sub(r"\d+(?:[.,]\d+)?\s*KV[A-Z]?", " ", text)
    text = re.sub(r"\([A-Z0-9]+\)", " ", text)
    text = re.sub(r"[^A-Z0-9]+", " ", text)
    return " ".join(text.split())


def build_unique_substations(source: pd.DataFrame) -> pd.DataFrame:
    df = source.copy()
    for column in ("val_niveltensao", "val_latitude", "val_longitude"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    stations = (
        df.groupby("id_subestacao", dropna=False)
        .agg(
            nom_subestacao=("nom_subestacao", "first"),
            id_estado=("id_estado", "first"),
            nom_estado=("nom_estado", "first"),
            id_subsistema=("id_subsistema", "first"),
            nom_subsistema=("nom_subsistema", "first"),
            max_voltage_kv=("val_niveltensao", "max"),
            latitude=("val_latitude", "first"),
            longitude=("val_longitude", "first"),
            voltage_levels=(
                "val_niveltensao",
                lambda values: "|".join(
                    f"{value:g}"
                    for value in sorted(set(values.dropna()))
                ),
            ),
            source_rows=("id_subestacao", "size"),
        )
        .reset_index()
    )

    stations["coordinate_valid"] = (
        stations["latitude"].between(-35, 6)
        & stations["longitude"].between(-75, -30)
    )
    return stations


def station_geodataframe(stations: pd.DataFrame) -> gpd.GeoDataFrame:
    valid = stations.loc[stations["coordinate_valid"]].copy()
    return gpd.GeoDataFrame(
        valid,
        geometry=gpd.points_from_xy(valid["longitude"], valid["latitude"]),
        crs="EPSG:4326",
    ).to_crs(TARGET_CRS)


def nearest_station(
    origins_projected: gpd.GeoDataFrame,
    stations: gpd.GeoDataFrame,
    prefix: str,
) -> pd.DataFrame:
    targets = stations.to_crs(DISTANCE_CRS)[
        ["id_subestacao", "nom_subestacao", "max_voltage_kv", "geometry"]
    ]
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
    return pd.DataFrame(
        {
            "ibge_code": joined["ibge_code"].astype("string"),
            f"{prefix}_distance_km": joined["_distance_m"] / 1000,
            f"{prefix}_id": joined["id_subestacao"],
            f"{prefix}_name": joined["nom_subestacao"],
            f"{prefix}_voltage_kv": joined["max_voltage_kv"],
        }
    )


def substation_counts(
    origins_projected: gpd.GeoDataFrame,
    stations: gpd.GeoDataFrame,
    minimum_voltage_kv: float,
    label: str,
) -> pd.DataFrame:
    targets = stations.loc[
        stations["max_voltage_kv"].ge(minimum_voltage_kv)
    ].to_crs(DISTANCE_CRS)

    result = pd.DataFrame(
        {"ibge_code": origins_projected["ibge_code"].astype("string")}
    )
    for radius_km in (25, 50):
        buffers = origins_projected[["ibge_code", "geometry"]].copy()
        buffers["geometry"] = buffers.geometry.buffer(radius_km * 1000)
        joined = gpd.sjoin(
            targets[["geometry"]],
            buffers,
            how="inner",
            predicate="within",
        )
        counts = joined.groupby("ibge_code").size()
        result[f"{label}_within_{radius_km}km"] = (
            result["ibge_code"].map(counts).fillna(0).astype(int)
        )
    return result


def build_epe_name_lookup(path: str | Path) -> gpd.GeoDataFrame:
    epe = gpd.read_file(path)
    if epe.crs is None:
        epe = epe.set_crs(TARGET_CRS)
    epe = epe.to_crs(TARGET_CRS)
    epe["clean_name"] = epe["Nome"].map(clean_station_name)
    counts = epe["clean_name"].value_counts()
    unique_names = counts[counts.eq(1)].index
    return epe.loc[epe["clean_name"].isin(unique_names)].set_index(
        "clean_name"
    )


def connection_points(
    source: pd.DataFrame,
    technology: str,
    stations: pd.DataFrame,
    epe_lookup: gpd.GeoDataFrame,
    municipalities: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    points = (
        source.loc[source["id_estado"].isin(NE_STATES), [
            "id_pontoconexao",
            "nom_pontoconexao",
            "id_estado",
        ]]
        .drop_duplicates()
        .copy()
    )
    points["technology"] = technology

    station_ids = sorted(
        stations["id_subestacao"].dropna().astype(str).unique(),
        key=len,
        reverse=True,
    )
    station_lookup = stations.set_index("id_subestacao")

    def prefix_station(value: object) -> str | None:
        point_id = str(value)
        for station_id in station_ids:
            if point_id.startswith(station_id):
                return station_id
        return None

    points["ons_station_id"] = points["id_pontoconexao"].map(prefix_station)
    points["latitude"] = points["ons_station_id"].map(
        lambda station_id: (
            station_lookup.loc[station_id, "latitude"]
            if station_id in station_lookup.index
            else np.nan
        )
    )
    points["longitude"] = points["ons_station_id"].map(
        lambda station_id: (
            station_lookup.loc[station_id, "longitude"]
            if station_id in station_lookup.index
            else np.nan
        )
    )

    valid = (
        points["latitude"].between(-35, 6)
        & points["longitude"].between(-75, -30)
    )
    points["geocode_method"] = np.where(
        valid,
        "ons_station_id_prefix",
        "unresolved",
    )

    for index, row in points.loc[
        points["geocode_method"].eq("unresolved")
    ].iterrows():
        clean_name = clean_station_name(row["nom_pontoconexao"])
        if clean_name not in epe_lookup.index:
            continue
        match = epe_lookup.loc[clean_name]
        points.at[index, "latitude"] = match.geometry.y
        points.at[index, "longitude"] = match.geometry.x
        points.at[index, "geocode_method"] = "epe_exact_name_fallback"

    resolved = points["geocode_method"].ne("unresolved")
    geocoded = gpd.GeoDataFrame(
        points.loc[resolved].copy(),
        geometry=gpd.points_from_xy(
            points.loc[resolved, "longitude"],
            points.loc[resolved, "latitude"],
        ),
        crs="EPSG:4326",
    ).to_crs(TARGET_CRS)

    joined = gpd.sjoin(
        geocoded,
        municipalities[["ibge_code", "municipality", "state", "geometry"]],
        how="left",
        predicate="within",
    ).drop(columns="index_right", errors="ignore")
    joined["state_matches_ibge"] = (
        joined["ibge_code"].notna()
        & joined["id_estado"].eq(joined["state"])
    )

    if (~resolved).any():
        unresolved = points.loc[~resolved].copy()
        unresolved["ibge_code"] = pd.NA
        unresolved["municipality"] = pd.NA
        unresolved["state"] = pd.NA
        unresolved["state_matches_ibge"] = False
        unresolved = gpd.GeoDataFrame(
            unresolved,
            geometry=[None] * len(unresolved),
            crs=TARGET_CRS,
        )
        joined = pd.concat([joined, unresolved], ignore_index=True)
        joined = gpd.GeoDataFrame(joined, geometry="geometry", crs=TARGET_CRS)

    return joined


def aggregate_curtailment(
    source: pd.DataFrame,
    points: gpd.GeoDataFrame,
    prefix: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = source.loc[source["id_estado"].isin(NE_STATES)].copy()
    numeric = [
        "val_geracaonaorealizadaapurada",
        "val_geracaoreferencia",
        "num_minutos_restricao",
        "num_minutos_rel",
        "num_minutos_cnf",
        "num_minutos_ene",
    ]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    map_columns = [
        "id_pontoconexao",
        "ibge_code",
        "municipality",
        "state",
        "geocode_method",
    ]
    mapping = (
        pd.DataFrame(points.drop(columns="geometry", errors="ignore"))[
            map_columns
        ]
        .drop_duplicates("id_pontoconexao")
    )
    data = data.merge(
        mapping,
        on="id_pontoconexao",
        how="left",
        suffixes=("", "_ibge"),
    )
    data["_restricted"] = data["num_minutos_restricao"].fillna(0).gt(0)
    data["_nonrealized"] = data[
        "val_geracaonaorealizadaapurada"
    ].fillna(0)
    data["_reference"] = data["val_geracaoreferencia"].fillna(0)

    geocoded = data.loc[data["ibge_code"].notna()].copy()
    result = (
        geocoded.groupby("ibge_code")
        .agg(
            asset_intervals=("id_ons", "size"),
            restricted_asset_intervals=("_restricted", "sum"),
            restriction_asset_minutes=("num_minutos_restricao", "sum"),
            restriction_rel_asset_minutes=("num_minutos_rel", "sum"),
            restriction_cnf_asset_minutes=("num_minutos_cnf", "sum"),
            restriction_ene_asset_minutes=("num_minutos_ene", "sum"),
            reported_nonrealized_mw_interval_sum=("_nonrealized", "sum"),
            reference_mw_interval_sum=("_reference", "sum"),
            ons_plants=("id_ons", "nunique"),
            connection_points=("id_pontoconexao", "nunique"),
        )
        .reset_index()
    )
    result = result.rename(
        columns={
            column: f"{prefix}_{column}"
            for column in result.columns
            if column != "ibge_code"
        }
    )
    result[f"{prefix}_restricted_interval_share"] = (
        result[f"{prefix}_restricted_asset_intervals"]
        / result[f"{prefix}_asset_intervals"]
    )
    denominator = result[f"{prefix}_reference_mw_interval_sum"]
    result[f"{prefix}_reported_nonrealized_to_reference_ratio"] = np.where(
        denominator.gt(0),
        result[f"{prefix}_reported_nonrealized_mw_interval_sum"] / denominator,
        np.nan,
    )
    return result, data


def connection_point_summary(
    enriched: pd.DataFrame,
    points: gpd.GeoDataFrame,
    technology: str,
) -> pd.DataFrame:
    summary = (
        enriched.groupby("id_pontoconexao")
        .agg(
            asset_intervals=("id_ons", "size"),
            restricted_asset_intervals=("_restricted", "sum"),
            restriction_asset_minutes=("num_minutos_restricao", "sum"),
            restriction_rel_asset_minutes=("num_minutos_rel", "sum"),
            restriction_cnf_asset_minutes=("num_minutos_cnf", "sum"),
            restriction_ene_asset_minutes=("num_minutos_ene", "sum"),
            reported_nonrealized_mw_interval_sum=("_nonrealized", "sum"),
            reference_mw_interval_sum=("_reference", "sum"),
            ons_plants=("id_ons", "nunique"),
        )
        .reset_index()
    )
    summary["reported_nonrealized_to_reference_ratio"] = np.where(
        summary["reference_mw_interval_sum"].gt(0),
        summary["reported_nonrealized_mw_interval_sum"]
        / summary["reference_mw_interval_sum"],
        np.nan,
    )

    point_table = pd.DataFrame(
        points.drop(columns="geometry", errors="ignore")
    )[
        [
            "id_pontoconexao",
            "nom_pontoconexao",
            "id_estado",
            "ons_station_id",
            "latitude",
            "longitude",
            "geocode_method",
            "ibge_code",
            "municipality",
            "state",
        ]
    ].drop_duplicates("id_pontoconexao")
    output = point_table.merge(summary, on="id_pontoconexao", how="left")
    output.insert(0, "technology", technology)
    return output


def state_summary(enriched: pd.DataFrame, technology: str) -> pd.DataFrame:
    result = (
        enriched.groupby(["id_estado", "nom_estado"])
        .agg(
            asset_intervals=("id_ons", "size"),
            restricted_asset_intervals=("_restricted", "sum"),
            restriction_asset_minutes=("num_minutos_restricao", "sum"),
            reported_nonrealized_mw_interval_sum=("_nonrealized", "sum"),
            reference_mw_interval_sum=("_reference", "sum"),
            ons_plants=("id_ons", "nunique"),
            connection_points=("id_pontoconexao", "nunique"),
        )
        .reset_index()
    )
    result["restricted_interval_share"] = (
        result["restricted_asset_intervals"] / result["asset_intervals"]
    )
    result["reported_nonrealized_to_reference_ratio"] = np.where(
        result["reference_mw_interval_sum"].gt(0),
        result["reported_nonrealized_mw_interval_sum"]
        / result["reference_mw_interval_sum"],
        np.nan,
    )
    result.insert(0, "technology", technology)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--municipalities",
        default="data/processed/ibge_northeast_municipalities.parquet",
    )
    parser.add_argument(
        "--epe-existing-substations",
        default="data/raw/epe/epe_subestacoes_base_existente.geojson",
    )
    parser.add_argument(
        "--ons-substations",
        default="data/raw/ons/ons_subestacoes_operacao.csv",
    )
    parser.add_argument(
        "--wind",
        default="data/raw/ons/ons_wind_curtailment_2026-10.csv",
    )
    parser.add_argument(
        "--solar",
        default="data/raw/ons/ons_solar_curtailment_2026-10.csv",
    )
    parser.add_argument("--period", default="2026-10")
    parser.add_argument("--output-dir", default="data/processed")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    municipalities = gpd.read_parquet(args.municipalities).to_crs(TARGET_CRS)
    municipalities["ibge_code"] = municipalities["ibge_code"].astype("string")

    sub_source = read_ons_csv(args.ons_substations)
    wind_source = read_ons_csv(args.wind)
    solar_source = read_ons_csv(args.solar)

    stations = build_unique_substations(sub_source)
    stations.to_csv(
        output / "ons_operating_substations_unique.csv",
        index=False,
    )
    stations_geo = station_geodataframe(stations)

    station_ne = stations_geo.loc[
        stations_geo["id_estado"].isin(NE_STATES)
    ].copy()
    station_ne = gpd.sjoin(
        station_ne,
        municipalities[
            ["ibge_code", "municipality", "state", "geometry"]
        ],
        how="left",
        predicate="within",
    ).drop(columns="index_right", errors="ignore")
    station_ne["state_matches_ibge"] = (
        station_ne["ibge_code"].notna()
        & station_ne["id_estado"].eq(station_ne["state"])
    )
    station_ne.to_file(
        output / "ons_operating_substations_northeast.gpkg",
        driver="GPKG",
    )

    origins = municipalities[
        ["ibge_code", "municipality", "state", "geometry"]
    ].copy()
    origins["geometry"] = origins.geometry.representative_point()
    origins_projected = origins.to_crs(DISTANCE_CRS)

    metrics = origins[["ibge_code", "municipality", "state"]].copy()
    metrics = metrics.merge(
        nearest_station(
            origins_projected,
            stations_geo,
            "nearest_ons_operating_substation",
        ),
        on="ibge_code",
        how="left",
    )
    metrics = metrics.merge(
        nearest_station(
            origins_projected,
            stations_geo.loc[stations_geo["max_voltage_kv"].ge(230)],
            "nearest_ons_operating_230kv_substation",
        ),
        on="ibge_code",
        how="left",
    )
    for minimum_voltage, label in (
        (69, "ons_operating_substations"),
        (230, "ons_operating_230kv_substations"),
    ):
        metrics = metrics.merge(
            substation_counts(
                origins_projected,
                stations_geo,
                minimum_voltage,
                label,
            ),
            on="ibge_code",
            how="left",
        )

    epe_lookup = build_epe_name_lookup(args.epe_existing_substations)
    wind_points = connection_points(
        wind_source,
        "wind",
        stations,
        epe_lookup,
        municipalities,
    )
    solar_points = connection_points(
        solar_source,
        "solar",
        stations,
        epe_lookup,
        municipalities,
    )

    wind_agg, wind_enriched = aggregate_curtailment(
        wind_source, wind_points, "wind"
    )
    solar_agg, solar_enriched = aggregate_curtailment(
        solar_source, solar_points, "solar"
    )

    for aggregate in (wind_agg, solar_agg):
        metrics = metrics.merge(aggregate, on="ibge_code", how="left")
        value_columns = [
            column for column in aggregate.columns if column != "ibge_code"
        ]
        metrics[value_columns] = metrics[value_columns].fillna(0)

    if len(metrics) != len(municipalities):
        raise ValueError(
            f"ONS output has {len(metrics)} rows; "
            f"expected {len(municipalities)}"
        )

    metrics.to_csv(
        output / f"ons_municipality_operational_metrics_{args.period}.csv",
        index=False,
    )

    wind_cp = connection_point_summary(
        wind_enriched, wind_points, "wind"
    )
    solar_cp = connection_point_summary(
        solar_enriched, solar_points, "solar"
    )
    connection_table = pd.concat(
        [wind_cp, solar_cp],
        ignore_index=True,
    )
    connection_table.to_csv(
        output / f"ons_curtailment_connection_points_{args.period}.csv",
        index=False,
    )
    connection_geo = connection_table.loc[
        connection_table["latitude"].notna()
        & connection_table["longitude"].notna()
    ].copy()
    connection_geo = gpd.GeoDataFrame(
        connection_geo,
        geometry=gpd.points_from_xy(
            connection_geo["longitude"],
            connection_geo["latitude"],
        ),
        crs="EPSG:4326",
    ).to_crs(TARGET_CRS)
    connection_geo.to_file(
        output / f"ons_curtailment_connection_points_{args.period}.gpkg",
        driver="GPKG",
    )

    pd.concat(
        [
            state_summary(wind_enriched, "wind"),
            state_summary(solar_enriched, "solar"),
        ],
        ignore_index=True,
    ).to_csv(
        output / f"ons_curtailment_state_summary_{args.period}.csv",
        index=False,
    )

    qa = pd.DataFrame(
        [
            ("ons_substation_source_rows", len(sub_source)),
            ("ons_unique_substations", len(stations)),
            (
                "ons_unique_substations_valid_coordinates",
                int(stations["coordinate_valid"].sum()),
            ),
            (
                "ons_unique_substations_ne_state",
                int(stations["id_estado"].isin(NE_STATES).sum()),
            ),
            (
                "ons_unique_substations_ne_valid_coordinates",
                len(station_ne),
            ),
            (
                "wind_source_rows_northeast",
                int(wind_source["id_estado"].isin(NE_STATES).sum()),
            ),
            (
                "wind_connection_points_northeast",
                len(wind_points),
            ),
            (
                "wind_connection_points_unresolved",
                int(wind_points["ibge_code"].isna().sum()),
            ),
            (
                "solar_source_rows_northeast",
                int(solar_source["id_estado"].isin(NE_STATES).sum()),
            ),
            (
                "solar_connection_points_northeast",
                len(solar_points),
            ),
            (
                "solar_connection_points_unresolved",
                int(solar_points["ibge_code"].isna().sum()),
            ),
            ("municipality_operational_metric_rows", len(metrics)),
        ],
        columns=["metric", "value"],
    )
    qa.to_csv(output / "ons_operational_qa.csv", index=False)

    print(f"ONS municipality rows: {len(metrics):,}")
    print(f"ONS unique operating substations: {len(stations):,}")
    print(
        "Wind connection points unresolved: "
        f"{wind_points['ibge_code'].isna().sum():,}"
    )
    print(
        "Solar connection points unresolved: "
        f"{solar_points['ibge_code'].isna().sum():,}"
    )
    print(
        "WARNING: constrained-off exposure is operational evidence only. "
        "Curtailment is not free electricity and does not prove connection "
        "capacity or contractual energy availability."
    )


if __name__ == "__main__":
    main()
