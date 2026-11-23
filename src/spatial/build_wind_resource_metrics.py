"""Build municipality-level Global Wind Atlas v4 resource metrics.

The input rasters are the lossless Northeast source subsets produced by
download_gwa_northeast.py. No resampling is performed before zonal statistics.

These are resource-potential indicators only. They do not represent actual
generation, PPA availability, dispatchability or connection capacity.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import geometry_mask, geometry_window


def zonal_metrics(
    municipalities: gpd.GeoDataFrame,
    raster_path: str | Path,
    prefix: str,
) -> pd.DataFrame:
    rows: list[dict] = []

    with rasterio.open(raster_path) as src:
        if src.crs is None:
            raise ValueError(f"Raster has no CRS: {raster_path}")
        polygons = municipalities.to_crs(src.crs)

        for record in polygons.itertuples():
            geometry = record.geometry
            result = {"ibge_code": str(record.ibge_code)}

            try:
                window = geometry_window(
                    src,
                    [geometry],
                    pad_x=0,
                    pad_y=0,
                )
            except Exception:
                result.update(
                    {
                        f"{prefix}_pixel_count": 0,
                        f"{prefix}_mean": np.nan,
                        f"{prefix}_median": np.nan,
                        f"{prefix}_p90": np.nan,
                        f"{prefix}_max": np.nan,
                    }
                )
                rows.append(result)
                continue

            data = src.read(1, window=window, masked=True)
            inside = geometry_mask(
                [geometry],
                out_shape=data.shape,
                transform=src.window_transform(window),
                invert=True,
                all_touched=False,
            )

            values = np.asarray(data.filled(np.nan), dtype="float64")
            values = values[inside & np.isfinite(values)]

            if src.nodata is not None:
                values = values[~np.isclose(values, src.nodata)]

            result[f"{prefix}_pixel_count"] = int(values.size)
            if values.size:
                result[f"{prefix}_mean"] = float(np.mean(values))
                result[f"{prefix}_median"] = float(np.median(values))
                result[f"{prefix}_p90"] = float(np.quantile(values, 0.90))
                result[f"{prefix}_max"] = float(np.max(values))
            else:
                result[f"{prefix}_mean"] = np.nan
                result[f"{prefix}_median"] = np.nan
                result[f"{prefix}_p90"] = np.nan
                result[f"{prefix}_max"] = np.nan

            rows.append(result)

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--municipalities",
        default="data/processed/ibge_northeast_municipalities.parquet",
    )
    parser.add_argument(
        "--wind-speed",
        default=(
            "data/raw/global_wind_atlas/"
            "gwa4_brazil_northeast_wind_speed_100m.tif"
        ),
    )
    parser.add_argument(
        "--power-density",
        default=(
            "data/raw/global_wind_atlas/"
            "gwa4_brazil_northeast_power_density_100m.tif"
        ),
    )
    parser.add_argument("--output-dir", default="data/processed")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    municipality_path = Path(args.municipalities)
    if municipality_path.suffix.lower() in {".parquet", ".pq"}:
        municipalities = gpd.read_parquet(municipality_path)
    else:
        municipalities = gpd.read_file(municipality_path)
    municipalities["ibge_code"] = municipalities["ibge_code"].astype("string")

    base = municipalities[
        ["ibge_code", "municipality", "state"]
    ].copy()

    speed = zonal_metrics(
        municipalities,
        args.wind_speed,
        "gwa_wind_speed_100m_mps",
    )
    density = zonal_metrics(
        municipalities,
        args.power_density,
        "gwa_power_density_100m_wm2",
    )

    result = (
        base.merge(speed, on="ibge_code", how="left")
        .merge(density, on="ibge_code", how="left")
    )

    if len(result) != len(municipalities):
        raise ValueError(
            f"Wind resource output has {len(result)} rows; "
            f"expected {len(municipalities)}"
        )

    result.to_csv(
        output / "gwa4_municipality_wind_resource_100m.csv",
        index=False,
    )

    qa = pd.DataFrame(
        [
            (
                "candidate_municipalities",
                len(result),
            ),
            (
                "municipalities_with_wind_speed_pixels",
                int(
                    result[
                        "gwa_wind_speed_100m_mps_pixel_count"
                    ].gt(0).sum()
                ),
            ),
            (
                "municipalities_with_power_density_pixels",
                int(
                    result[
                        "gwa_power_density_100m_wm2_pixel_count"
                    ].gt(0).sum()
                ),
            ),
            (
                "missing_wind_speed_mean",
                int(
                    result[
                        "gwa_wind_speed_100m_mps_mean"
                    ].isna().sum()
                ),
            ),
            (
                "missing_power_density_mean",
                int(
                    result[
                        "gwa_power_density_100m_wm2_mean"
                    ].isna().sum()
                ),
            ),
        ],
        columns=["metric", "value"],
    )
    qa.to_csv(
        output / "gwa4_wind_resource_qa.csv",
        index=False,
    )

    print(f"Municipality wind resource rows: {len(result):,}")
    print(
        "Wind-speed coverage: "
        f"{result['gwa_wind_speed_100m_mps_mean'].notna().sum():,}"
    )
    print(
        "Power-density coverage: "
        f"{result['gwa_power_density_100m_wm2_mean'].notna().sum():,}"
    )
    print(
        "WARNING: Global Wind Atlas values describe climatological wind "
        "resource potential. They are not actual generation or contractual "
        "energy availability."
    )


if __name__ == "__main__":
    main()
