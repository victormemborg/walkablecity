import os
import pandas as pd
import pickle
import pygeohash as pgh
import pandana as pdna
import geopandas as gpd
from shapely.geometry import box
from sqlalchemy import create_engine
from dotenv import load_dotenv

# CONSTANTS
PRECISION_LEVELS = [3, 4, 5, 6, 7]
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

all_levels = []

for precision in PRECISION_LEVELS:
    print(f"Computing geohash precision {precision} / {max(PRECISION_LEVELS)} ...")

    hashes = [
        pgh.encode(latitude=lat, longitude=lon, precision=precision)
        for lat, lon in zip(scored_nodes["y"], scored_nodes["x"])
    ]

    level_df = scored_nodes[["score"]].copy()
    level_df["hash"] = hashes

    grouped = level_df.groupby("hash", as_index=False).agg({"score": "mean"})
    grouped["rectangle"] = grouped["hash"].apply(box_hash)
    grouped["level"] = precision

    gdf = gpd.GeoDataFrame(
        grouped[["level", "score"]],
        geometry=grouped["rectangle"],
        crs=4326,
    )
    gdf = gdf.rename_geometry("rectangle")

    all_levels.append(gdf)
    print(f"Constructed gdf with {len(gdf)} rows for precision {precision}.")

# POSTGIS OUTPUT
load_dotenv()
engine = create_engine(os.environ["DATABASE_URL"])

combined = pd.concat(all_levels, ignore_index=True)
combined = gpd.GeoDataFrame(combined, geometry="rectangle", crs=4326)

print(f"Writing {len(combined)} total grid rows to PostGIS ...")
combined.to_postgis(name="grid_multilevel", con=engine, if_exists="replace")
