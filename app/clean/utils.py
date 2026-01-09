from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile

from geopandas import GeoDataFrame
from shapely import get_point

from ..config import gdal_parquet_options


def cleaning(
    gdf0: GeoDataFrame,
    output_path: Path,
    output_layer: str,
    overwrite: str = "--overwrite-layer",
) -> None:
    """Generate attributes and dissolve polygons."""
    gdf = gdf0.copy()
    gdf = gdf.to_crs(4326)
    gdf["area_sqkm"] = gdf.geometry.to_crs(6933).area / 1_000_000
    gdf["center_lat"] = get_point(
        gdf.geometry.maximum_inscribed_circle(tolerance=0.000001),
        0,
    ).y
    gdf["center_lon"] = get_point(
        gdf.geometry.maximum_inscribed_circle(tolerance=0.000001),
        0,
    ).x
    with NamedTemporaryFile(suffix=".gpkg") as temp_file:
        gdf.to_file(temp_file.name)
        run(
            [
                *["gdal", "vector", "pipeline"],
                *["read", temp_file.name, "!"],
                *[
                    "set-field-type",
                    "--src-field-type=DateTime",
                    "--dst-field-type=Date",
                    "!",
                ],
                *[
                    "set-field-type",
                    "--field-name=valid_to",
                    "--dst-field-type=Date",
                    "!",
                ],
                *[
                    "write",
                    output_path,
                    f"--output-layer={output_layer}",
                    "--lco=TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER",
                    overwrite,
                    "--quiet",
                ],
            ],
            check=False,
        )


def convert(input_path: Path, input_layer: str, output_path: Path) -> None:
    """Make a file for pre-edge-matching."""
    run(
        [
            *["gdal", "vector", "convert"],
            *[input_path, output_path],
            f"--input-layer={input_layer}",
            *gdal_parquet_options,
        ],
        check=False,
    )


def get_columns(level_max: int, level_min: int) -> list[str]:
    """Get columns between two admin levels."""
    result = []
    for lvl in range(level_max, level_min, -1):
        result.extend(
            [
                f"adm{lvl}_name",
                f"adm{lvl}_name1",
                f"adm{lvl}_name2",
                f"adm{lvl}_name3",
                f"adm{lvl}_pcode",
            ],
        )
    return result


def pre_cleaning(input_path: Path, output_path: Path | str) -> None:
    """Apply automatic topology corrections."""
    run(
        [
            *["gdal", "vector", "pipeline"],
            *["read", input_path, "!"],
            *["reproject", "--dst-crs=EPSG:4326", "!"],
            *["set-geom-type", "--multi", "--dim=XY", "!"],
            *["clean-coverage", "!"],
            *["make-valid", "!"],
            *["write", output_path],
            *gdal_parquet_options,
        ],
        check=False,
    )
