import os
import pandas as pd
import pickle
import pygeohash as pgh
import pandana as pdna
import geopandas as gpd
from shapely.geometry import box
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# CONSTANTS
#TODO: We need to tune both on the precision levels and the zoom level thresholds. 
# Precision level 3 is probably too coarse for Denmark, but i'll leave it for now, since starting on precision level 4 with current zoom thresholds
# results in 50% increased api response times.
PRECISION_LEVELS = [4, 5, 6, 7] # https://medium.com/@zaenun.faiz/processing-large-geospatial-dataset-using-geohash-spatial-index-6f78079951d3
MAX_DIST = 1600  # meters

# INPUT
with open("data/intermediate/nearest_categories.pkl", "rb") as f:
    nearest_categories: dict[str, pd.DataFrame] = pickle.load(f)

network = pdna.Network.from_hdf5("data/intermediate/denmark.backup")

# SCORING LOGIC
dist_df = pd.concat(
    [df["dist"] for df in nearest_categories.values()],
    axis=1,
)

nodes = network.nodes_df
nodes["score"] = (dist_df <= MAX_DIST).sum(axis=1)
scored_nodes = nodes[nodes["score"] > 0].copy()

print(f"Scored nodes: {len(scored_nodes)}")

# BUILDING MULTI PRECISION LEVEL GRID
def box_hash(hash: str):
    min_lat, min_lon, max_lat, max_lon = pgh.get_bounding_box(hash)
    return box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)

# POSTGIS OUTPUT
load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

for precision in PRECISION_LEVELS:
    print(f"Computing geohash precision {precision} / {max(PRECISION_LEVELS)} ...")

    hashes = [
        pgh.encode(latitude=lat, longitude=lon, precision=precision)
        for lat, lon in zip(scored_nodes["y"], scored_nodes["x"])
    ]

    level_df = scored_nodes[["score"]].copy()
    level_df["hash"] = hashes

    grouped = level_df.groupby("hash", as_index=False).agg({"score": "mean"})
    grouped["geometry"] = grouped["hash"].apply(box_hash)

    final = grouped[["geometry", "score"]]
    gdf = gpd.GeoDataFrame(final, geometry="geometry", crs=4326)
    
    table_name = f"grid_precision_{precision}"
    gdf.to_postgis(name=table_name, con=engine, if_exists="replace")

    print(f"Created table {table_name} with {len(gdf)} rows for precision {precision}.")

print("DONE: All tables constructed in db.")
