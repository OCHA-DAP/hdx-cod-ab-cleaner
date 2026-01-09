from httpx import Client, Response
from tenacity import retry, stop_after_attempt, wait_fixed

from ..config import (
    ARCGIS_PASSWORD,
    ARCGIS_SERVER,
    ARCGIS_USERNAME,
    ATTEMPT,
    TIMEOUT,
    WAIT,
)


@retry(stop=stop_after_attempt(ATTEMPT), wait=wait_fixed(WAIT))
def client_get(url: str, params: dict | None = None) -> Response:
    """HTTP GET with retries, waiting, and longer timeouts."""
    with Client(http2=True, timeout=TIMEOUT) as client:
        return client.get(url, params=params)


def generate_token() -> str:
    """Generate a token for ArcGIS Server."""
    url = f"{ARCGIS_SERVER}/portal/sharing/rest/generateToken"
    data = {
        "username": ARCGIS_USERNAME,
        "password": ARCGIS_PASSWORD,
        "referer": f"{ARCGIS_SERVER}/portal",
        "f": "json",
    }
    with Client(http2=True) as client:
        r = client.post(url, data=data).json()
        return r["token"]


def parse_fields(fields: list) -> tuple[str, str]:
    """Extract the OBJECTID and field names from a config."""
    objectid_name = "esriFieldTypeOID"
    objectid = next(x["name"] for x in fields if x["type"] == objectid_name)
    field_names = ",".join(
        [
            x["name"]
            for x in fields
            if x["type"] != objectid_name
            and not x.get("virtual")
            and not x["name"].lower().startswith("objectid")
        ],
    )
    return objectid, field_names
