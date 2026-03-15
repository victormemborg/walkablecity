import os

from sqlalchemy import create_engine
from dotenv import load_dotenv
from dagster import asset, AssetIn, AssetKey, AssetExecutionContext, AssetsDefinition
from models.models import GeometryCollection, PostGISTable

def geometry_to_postgis_asset(upstream: AssetKey, partitions_def=None, schema="public"):
    """Returns a new PostGISTable asset from upstream GeometryCollection asset"""
    upstream_name = upstream.path[-1]

    @asset(
        name=f"{upstream_name}_postgis",
        ins={"geometry_collection": AssetIn(key=upstream)},
        partitions_def=partitions_def
    )
    def write_to_postgis(context: AssetExecutionContext, geometry_collection: GeometryCollection) -> PostGISTable:
        """The new PostGISTable asset"""

        load_dotenv()
        connection_str = os.environ["DATABASE_URL"]

        engine = create_engine(connection_str)
        table_name = f"{upstream_name}_precision_{geometry_collection.precision_level}"

        geometry_collection.geometry.to_postgis(name=table_name, con=engine, if_exists="replace")

        context.add_output_metadata({
            "table": table_name,
            "schema": schema,
            "rows": len(geometry_collection.geometry)
        })

        return PostGISTable(table_name, connection_str, schema)

    return write_to_postgis