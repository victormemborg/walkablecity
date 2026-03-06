import dagster as dg
import pandana as pdna
import pandas as pd
import pygeohash as pgh
import geopandas as gpd

from shapely.geometry import box

def box_hash(hash: str):
    min_lat, min_lon, max_lat, max_lon = pgh.get_bounding_box(hash)
    return box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)

@dg.asset(kinds={"python"})
async def scored_grids(context: dg.AssetExecutionContext, walk_network: pdna.Network, scored_nodes: pd.DataFrame) -> dict[int, gpd.GeoDataFrame]:
    """Aggregate scored nodes into grids and average their scores"""

    PRECISION_LEVELS = [4, 5, 6, 7] # https://medium.com/@zaenun.faiz/processing-large-geospatial-dataset-using-geohash-spatial-index-6f78079951d3
    grids: dict[int, gpd.GeoDataFrame] = {} # Precision level -> grid

    for level in PRECISION_LEVELS:
        context.log.info(f"Computing geohash precision {level} / {max(PRECISION_LEVELS)} ...")

        hashes = [
            pgh.encode(latitude=lat, longitude=lon, precision=level)
            for lat, lon in zip(scored_nodes["y"], scored_nodes["x"])
        ]

        level_df = scored_nodes[["score"]].copy()
        level_df["hash"] = hashes

        grouped = level_df.groupby("hash", as_index=False).agg({"score": "mean"})
        grouped["geometry"] = grouped["hash"].apply(box_hash)

        final = grouped[["geometry", "score"]]
        gdf = gpd.GeoDataFrame(final, geometry="geometry", crs=4326)
        
        grids[level] = gdf
        context.log.info(f"Created GeoDataFrame with {len(gdf)} rows for precision {level}.")

    return grids


    