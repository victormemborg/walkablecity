import os
import geopandas as gpd
import subprocess
import json
import threading

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

        proc = subprocess.Popen(
            ["tippecanoe", 
             "--minimum-zoom=0",
             "--maximum-zoom=18", 
             "--read-parallel", 
             f"--output={out_path}", 
             "--drop-densest-as-needed" ,
             "--force",
             "--no-progress-indicator",],
            stdin=subprocess.PIPE,
            text=True,
        )

        stdin = proc.stdin
        if stdin is None:
            raise AttributeError(stdin)

        try:
            for _, row in geometry.iterrows():
                feature = {
                    "type": "Feature",
                    "geometry": row.geometry.__geo_interface__,
                    "properties": row.drop("geometry").to_dict(),
                }

                stdin.write(json.dumps(feature) + "\n")

        finally:
            stdin.close()
        
        proc.wait()

        if proc.returncode != 0:
            raise RuntimeError("tippecanoe failed")

        return FileRef(out_path)

    return write_to_pmtiles