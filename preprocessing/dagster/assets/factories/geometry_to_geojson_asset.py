import os
import geopandas as gpd

from sqlalchemy import create_engine
from dotenv import load_dotenv
from dagster import asset, AssetIn, AssetKey, AssetExecutionContext, AssetsDefinition
from models.models import FileRef

def geometry_to_geojson_asset(upstream: AssetKey, partitions_def=None, schema="public"):
    """Returns a new GeoJSON asset from upstream GeoDataFrame asset"""
    upstream_name = upstream.path[-1]

    @asset(
        name=f"{upstream_name}_geojson",
        ins={"geometry": AssetIn(key=upstream)},
        partitions_def=partitions_def,
        kinds={"python"},
    )
    def write_to_geojson(context: AssetExecutionContext, geometry: gpd.GeoDataFrame) -> FileRef:
        """The new GeoJSON asset"""

        partition = context.partition_key if partitions_def else "0"
        file_name = f"{upstream_name}_{partition}"

        out_path = os.path.join(context.instance.storage_directory(), file_name)
        geometry.to_file(out_path, driver="GeoJSON")

        context.add_output_metadata({
            "rows": len(geometry)
        })

        return FileRef(out_path)

    return write_to_geojson