from pathlib import Path
from tempfile import NamedTemporaryFile

from geopandas import read_parquet

from ..config import data_dir
from .utils import cleaning, convert, get_columns, pre_cleaning


def clean_admin(input_path: Path) -> None:
    """Run main function."""
    level = int(input_path.stem[-1])
    iso3 = input_path.stem[:3].lower()
    output_path = data_dir / "outputs" / f"cod_ab_{iso3}.gdb"
    output_path.parent.mkdir(exist_ok=True)
    output_pre_em = data_dir / "tmp" / f"{input_path.stem}.parquet"
    output_pre_em.parent.mkdir(exist_ok=True)

    with NamedTemporaryFile(suffix=".parquet") as temp_file:
        pre_cleaning(input_path, temp_file.name)
        gdf = read_parquet(temp_file.name)
        gdf = gdf.drop(columns=[f"adm{level}_ref_name"], errors="ignore")
        gdf = gdf.sort_values(by=f"adm{level}_pcode")
        cleaning(gdf, output_path, f"{iso3}_admin{level}", overwrite="--overwrite")
        for lvl in range(level - 1, -1, -1):
            gdf1 = gdf.drop(columns=get_columns(level, lvl))
            gdf1["dissolve"] = gdf1[f"adm{lvl}_pcode"]
            gdf1 = gdf1.dissolve(by="dissolve")
            gdf1 = gdf1.reset_index(drop=True)
            cleaning(gdf1, output_path, f"{iso3}_admin{lvl}")
        convert(output_path, f"{iso3}_admin{level}", output_pre_em)


def clean_admin_em(input_path: Path) -> None:
    """Run main function."""
    level = int(input_path.stem[-1])
    iso3 = input_path.stem[:3].lower()
    output_em = data_dir / "tmp" / f"{input_path.stem}_em.parquet"
    output_path = data_dir / "outputs" / f"cod_ab_{iso3}.gdb"

    gdf = read_parquet(output_em)
    gdf_adm0 = read_parquet(
        data_dir / "tmp" / "bnda_cty.parquet",
        filters=[("iso3cd", "==", iso3.upper())],
    )
    gdf = gdf.clip(gdf_adm0)
    gdf = gdf.sort_values(by=f"adm{level}_pcode")

    cleaning(gdf, output_path, f"{iso3}_admin{level}_em")
    for lvl in range(level - 1, -1, -1):
        gdf1 = gdf.drop(columns=get_columns(level, lvl))
        gdf1["dissolve"] = gdf1[f"adm{lvl}_pcode"]
        gdf1 = gdf1.dissolve(by="dissolve")
        gdf1 = gdf1.reset_index(drop=True)
        cleaning(gdf1, output_path, f"{iso3}_admin{lvl}_em")

    (data_dir / "tmp" / f"{input_path.stem}.parquet").unlink()
    output_em.unlink()
