import dagster as dg
import httpx

from pathlib import Path
from models.models import RawPBF

URL = "https://download.geofabrik.de/europe/denmark-latest.osm.pbf"
DATA_DIR = Path("../data")
DATA_DIR.mkdir(exist_ok=True)


@dg.asset(kinds={"python"})
async def denmark_raw(context: dg.AssetExecutionContext) -> RawPBF:
    """Download the latest version of denmark.osm.pbf from Geofabrik"""

    out_path = DATA_DIR / "denmark-latest.osm.pbf"
    if out_path.exists():
        context.log.info(f"{out_path} already exists. Reusing asset...")
        return RawPBF(out_path)

    context.log.info(f"Downloading {URL} ...")

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", URL) as response:
            response.raise_for_status()

            with open(out_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

    context.log.info(f"Saved to {out_path}")
    return RawPBF(out_path)