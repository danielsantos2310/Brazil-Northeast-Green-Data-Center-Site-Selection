"""Split Northeast GWA source subsets into lossless per-state raster windows.

The state bounds below are derived from the official IBGE 2025 municipal mesh
used in Step 04. Each window has a 0.05-degree buffer so all boundary pixels
required for municipality zonal statistics are retained.

These files remain derivative source subsets, not original national GWA TIFFs.
No resampling is performed.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import rasterio
from rasterio.windows import from_bounds

STATE_BOUNDS_EPSG4674 = {
    "AL": [-38.2375896, -10.5004477, -35.1518917, -8.8131279],
    "BA": [-46.57728461, -18.3485603, -37.3411467, -8.5328206],
    "CE": [-41.4235180, -7.8581820, -37.2526586, -2.7843235],
    "MA": [-48.7551507, -10.2617647, -41.7960691, -1.0493281],
    "PB": [-38.7656034, -8.3029549, -34.7930865, -6.0259119],
    "PE": [-41.3583362, -9.4828974, -32.3777679, -3.8046222],
    "PI": [-46.0282068, -10.9287563, -40.3705098, -2.7497526],
    "RN": [-38.5820985, -6.9827348, -34.9684540, -4.8163592],
    "SE": [-38.2450090, -11.5685896, -36.3959408, -9.5150299],
}
BUFFER_DEGREES = 0.05


def clip_window(
    source_path: Path,
    output_path: Path,
    bounds: list[float],
) -> dict:
    buffered = [
        bounds[0] - BUFFER_DEGREES,
        bounds[1] - BUFFER_DEGREES,
        bounds[2] + BUFFER_DEGREES,
        bounds[3] + BUFFER_DEGREES,
    ]
    with rasterio.open(source_path) as src:
        if src.crs is None or src.crs.to_epsg() != 4326:
            raise ValueError(
                f"Expected EPSG:4326 source raster, found {src.crs}"
            )

        window = from_bounds(
            *buffered,
            transform=src.transform,
        ).round_offsets().round_lengths()
        window = window.intersection(
            rasterio.windows.Window(0, 0, src.width, src.height)
        )
        data = src.read(window=window)
        profile = src.profile.copy()
        profile.update(
            width=int(window.width),
            height=int(window.height),
            transform=src.window_transform(window),
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(data)

        return {
            "ibge_state_bounds_epsg4674": bounds,
            "buffer_degrees": BUFFER_DEGREES,
            "subset_bounds_epsg4326": list(
                rasterio.windows.bounds(window, src.transform)
            ),
            "width": int(window.width),
            "height": int(window.height),
            "bytes": output_path.stat().st_size,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        default="gwa_raw",
    )
    parser.add_argument(
        "--output-dir",
        default="gwa_states",
    )
    args = parser.parse_args()

    source = Path(args.source_dir)
    output = Path(args.output_dir)
    source_manifest = source / "gwa4_northeast_manifest.json"

    rasters = {
        "wind_speed_100m": (
            source / "gwa4_brazil_northeast_wind_speed_100m.tif"
        ),
        "power_density_100m": (
            source / "gwa4_brazil_northeast_power_density_100m.tif"
        ),
    }
    for path in rasters.values():
        if not path.exists():
            raise FileNotFoundError(path)

    for state, bounds in STATE_BOUNDS_EPSG4674.items():
        state_dir = output / state
        state_dir.mkdir(parents=True, exist_ok=True)
        state_manifest = {
            "state": state,
            "subset_type": "lossless_raster_window",
            "source_manifest": "gwa4_northeast_manifest.json",
            "resources": [],
        }

        for resource_name, path in rasters.items():
            out_path = state_dir / (
                f"gwa4_{state.lower()}_{resource_name}.tif"
            )
            metadata = clip_window(path, out_path, bounds)
            state_manifest["resources"].append(
                {
                    "resource": resource_name,
                    "filename": out_path.name,
                    **metadata,
                }
            )

        shutil.copy2(
            source_manifest,
            state_dir / "gwa4_northeast_manifest.json",
        )
        (state_dir / "gwa4_state_subset_manifest.json").write_text(
            json.dumps(state_manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(
            state,
            sum(item["bytes"] for item in state_manifest["resources"]),
        )


if __name__ == "__main__":
    main()
