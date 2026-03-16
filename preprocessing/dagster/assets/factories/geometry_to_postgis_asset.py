import os
import geopandas as gpd

from sqlalchemy import create_engine
from dotenv import load_dotenv
from dagster import asset, AssetIn, AssetKey, AssetExecutionContext, AssetsDefinition
from models.models import PostGISTable

def geometry_to_postgis_asset(upstream: AssetKey, partitions_def=None, schema="public"):
    """Returns a new PostGIS asset from upstream GeoDataFrame asset"""
    upstream_name = upstream.path[-1]

    @asset(
        name=f"{upstream_name}_postgis",
        ins={"geometry": AssetIn(key=upstream)},
        partitions_def=partitions_def,
        kinds={"python"},
    )
    def write_to_postgis(context: AssetExecutionContext, geometry: gpd.GeoDataFrame) -> PostGISTable:
        """The new PostGIS asset"""

        load_dotenv()
        connection_str = os.environ["DATABASE_URL"]
        partition = context.partition_key if partitions_def else "0"

        engine = create_engine(connection_str)
        table_name = f"{upstream_name}_precision_{partition}"

        geometry.to_postgis(name=table_name, con=engine, if_exists="replace")

        context.add_output_metadata({
            "table": table_name,
            "schema": schema,
            "rows": len(geometry)
        })

        return PostGISTable(table_name, connection_str, schema)

    return write_to_postgis