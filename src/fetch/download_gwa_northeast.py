"""Create lossless Northeast Brazil subsets from Global Wind Atlas v4 country TIFFs.

The official Brazil rasters are ~0.5 GB each. This script uses GDAL HTTP range
reads to extract only the Step 04 IBGE Northeast bounding box, plus a small
buffer, without downloading the entire national rasters.

Outputs are explicitly derivative source subsets, not unmodified raw national
files. The manifest records original URLs, reported national byte sizes,
source raster metadata, clip bounds and SHA-256 checksums.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds

GWA_API = "https://globalwindatlas.info/api/gis/country/BRA"
RESOURCES = {
    "wind_speed_100m": f"{GWA_API}/wind-speed/100",
    "power_density_100m": f"{GWA_API}/power-density/100",
}
# Exact Step 04 IBGE Northeast municipality extent, buffered by 0.10 degree.
NE_BOUNDS_EPSG4674 = (
    -48.8551507,
    -18.4485603,
    -32.2777679,
    -0.9493281,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_source(url: str) -> tuple[str, int | None]:
    with requests.get(
        url,
        headers={"Range": "bytes=0-0", "User-Agent": "Mozilla/5.0"},
        stream=True,
        timeout=120,
        allow_redirects=True,
    ) as response:
        response.raise_for_status()
        content_range = response.headers.get("content-range")
        total_bytes = None
        if content_range and "/" in content_range:
            total_bytes = int(content_range.rsplit("/", 1)[1])
        return response.url, total_bytes


def clip_remote_tiff(
    source_url: str,
    output_path: Path,
) -> dict:
    vsi_url = f"/vsicurl/{source_url}"
    with rasterio.Env(
        GDAL_HTTP_MULTIRANGE="YES",
        GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    ):
        with rasterio.open(vsi_url) as src:
            if src.crs is None:
                raise ValueError(f"Source raster has no CRS: {source_url}")

            source_bounds = transform_bounds(
                "EPSG:4674",
                src.crs,
                *NE_BOUNDS_EPSG4674,
                densify_pts=21,
            )
            window = from_bounds(
                *source_bounds,
                transform=src.transform,
            ).round_offsets().round_lengths()
            window = window.intersection(
                rasterio.windows.Window(
                    0, 0, src.width, src.height
                )
            )

            data = src.read(window=window)
            transform = src.window_transform(window)
            profile = src.profile.copy()
            profile.update(
                width=int(window.width),
                height=int(window.height),
                transform=transform,
                compress="deflate",
                predictor=2,
                tiled=True,
                BIGTIFF="IF_SAFER",
            )

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(data)
                if src.nodata is not None:
                    dst.nodata = src.nodata

            return {
                "source_crs": src.crs.to_string(),
                "source_width": src.width,
                "source_height": src.height,
                "source_bounds": list(src.bounds),
                "source_dtype": src.dtypes[0],
                "source_nodata": src.nodata,
                "source_count": src.count,
                "source_resolution": list(src.res),
                "subset_window": {
                    "col_off": int(window.col_off),
                    "row_off": int(window.row_off),
                    "width": int(window.width),
                    "height": int(window.height),
                },
                "subset_bounds_source_crs": list(
                    rasterio.windows.bounds(window, src.transform)
                ),
            }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="data/raw/global_wind_atlas",
    )
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    manifest = {
        "provider": "Global Wind Atlas",
        "version": "4.0",
        "country": "Brazil",
        "height_m": 100,
        "subset_type": "lossless_raster_window_from_official_country_tiff",
        "ibge_northeast_bounds_epsg4674_buffered": list(
            NE_BOUNDS_EPSG4674
        ),
        "resources": [],
    }

    for name, api_url in RESOURCES.items():
        print(f"Resolving {name}")
        final_url, national_bytes = resolve_source(api_url)
        output_path = output / f"gwa4_brazil_northeast_{name}.tif"
        metadata = clip_remote_tiff(final_url, output_path)
        row = {
            "name": name,
            "api_url": api_url,
            "resolved_source_url": final_url,
            "reported_national_bytes": national_bytes,
            "subset_filename": output_path.name,
            "subset_bytes": output_path.stat().st_size,
            "subset_sha256": sha256(output_path),
            **metadata,
        }
        manifest["resources"].append(row)
        print(
            name,
            "national_bytes=", national_bytes,
            "subset_bytes=", row["subset_bytes"],
            "window=", row["subset_window"],
        )

    manifest_path = output / "gwa4_northeast_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
