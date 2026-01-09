import logging
from os import environ, getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

environ["OGR_GEOJSON_MAX_OBJ_SIZE"] = "0"
environ["OGR_ORGANIZE_POLYGONS"] = "ONLY_CCW"
environ["PYOGRIO_USE_ARROW"] = "1"

ARCGIS_SERVER = getenv("ARCGIS_SERVER", "https://gis.unocha.org")
ARCGIS_USERNAME = getenv("ARCGIS_USERNAME", "")
ARCGIS_PASSWORD = getenv("ARCGIS_PASSWORD", "")
ARCGIS_FOLDER = getenv("ARCGIS_FOLDER", "Hosted")
ARCGIS_SERVICE_URL = f"{ARCGIS_SERVER}/server/rest/services/{ARCGIS_FOLDER}"
ARCGIS_ADM0_URL = f"{ARCGIS_SERVICE_URL}/Global_AB_1M_fs_gray/FeatureServer/5"

ATTEMPT = int(getenv("ATTEMPT", "5"))
WAIT = int(getenv("WAIT", "10"))
TIMEOUT = int(getenv("TIMEOUT", "60"))

cwd = Path(__file__).parent
data_dir = cwd / "../data"

gdal_parquet_options = [
    "--overwrite",
    "--quiet",
    "--lco=USE_PARQUET_GEO_TYPES=YES",
    "--lco=COMPRESSION_LEVEL=15",
    "--lco=COMPRESSION=ZSTD",
]
