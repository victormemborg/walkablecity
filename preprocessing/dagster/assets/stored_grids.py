import os
import dagster as dg
import geopandas as gpd

from sqlalchemy import create_engine
from dotenv import load_dotenv

@dg.asset(kinds={"python"})
async def stored_grids(context: dg.AssetExecutionContext, scored_grids: dict[int, gpd.GeoDataFrame]):
    """Stores the given grids in a PostGIS database"""

    load_dotenv()
    engine = create_engine(os.environ["DATABASE_URL"])

    for level, grid in scored_grids.items():
        table_name = f"grid_precision_{level}"
        grid.to_postgis(name=table_name, con=engine, if_exists="replace")