import os
import dagster as dg
import httpx

from models.models import FileRef
from resources.global_config import GlobalConfig

@dg.asset(kinds={"python"})
async def country_osm(context: dg.AssetExecutionContext, global_config: GlobalConfig) -> FileRef:
    """Download a .osm.pbf country extract from a URL specified in GlobalConfig"""

    url = global_config.country_url
    out_path = os.path.join(context.instance.storage_directory(), "country-latest.osm.pbf")
    context.log.info(f"Downloading {url} ...")

    async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(out_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)

    context.log.info(f"Saved to {out_path}")
    return FileRef(out_path)