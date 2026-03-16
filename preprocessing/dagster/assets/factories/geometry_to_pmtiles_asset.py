import os
import geopandas as gpd
import subprocess
import json
import threading
import tempfile

from dagster import asset, AssetIn, AssetKey, AssetExecutionContext
from models.models import FileRef


def geometry_to_pmtiles_asset(upstream: AssetKey, partitions_def=None):
    """Returns a new PMTiles archive asset from upstream GeoDataFrame asset"""
    upstream_name = upstream.path[-1]
    asset_name = f"{upstream_name}_pmtiles"

    @asset(
        name=asset_name,
        ins={"geometry": AssetIn(key=upstream)},
        partitions_def=partitions_def,
        kinds={"python"},
    )
    def write_to_pmtiles(context: AssetExecutionContext, geometry: gpd.GeoDataFrame) -> FileRef:
        """The new PMTiles archive asset"""

        precision = context.partition_key if partitions_def else "0"
        file_name = f"{asset_name}_p{precision}.pmtiles"
        out_path = os.path.join(context.instance.storage_directory(), file_name)

        with tempfile.NamedTemporaryFile(suffix=".geojson", delete=False) as tmp:
            tmp_path = tmp.name

        geometry.to_file(tmp_path, driver="GeoJSON")

        proc = subprocess.run(
            ["tippecanoe", 
             f"--output={out_path}",
             "--minimum-zoom=0",
             "--maximum-zoom=18", 
             "--read-parallel",  
             "--drop-densest-as-needed" ,
             "--force",
             "--no-progress-indicator",
             "--simplification=10",
             "--hilbert",
             tmp_path],
            check=True,
        )

        os.remove(tmp_path)
        proc.check_returncode()

        return FileRef(out_path)

    return write_to_pmtiles