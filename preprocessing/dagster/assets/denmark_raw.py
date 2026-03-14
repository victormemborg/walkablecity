import os
import dagster as dg
import httpx

from models.models import FileRef

URL = "https://download.geofabrik.de/europe/denmark-latest.osm.pbf"

@dg.asset(kinds={"python"})
async def denmark_raw(context: dg.AssetExecutionContext) -> FileRef:
    """Download the latest version of denmark.osm.pbf from Geofabrik"""

    base_dir = os.path.join(context.instance.storage_directory(), "storage")
    out_path = os.path.join(base_dir, "denmark-latest.osm.pbf")

    context.log.info(f"Downloading {URL} ...")

    async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
        async with client.stream("GET", URL) as response:
            response.raise_for_status()

            with open(out_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

    context.log.info(f"Saved to {out_path}")
    return FileRef(out_path)