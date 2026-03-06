import os
import dagster as dg
import geopandas as gpd

from sqlalchemy import create_engine
from dotenv import load_dotenv

@dg.asset(kinds={"python"}, io_manager_key="pandana_io_manager")
async def stored_edges(context: dg.AssetExecutionContext, scored_edges: gpd.GeoDataFrame):
    """Stores the given edges in a PostGIS database"""

    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])

    scored_edges.to_postgis(name="edges", con=engine, if_exists="replace")