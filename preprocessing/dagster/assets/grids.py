import dagster as dg
import pandas as pd
import pygeohash as pgh
import geopandas as gpd

from shapely.geometry import box
from models.models import GeometryCollection
from assets.factories.geometry_to_postgis_asset import geometry_to_postgis_asset


PRECISION_LEVELS = ["4", "5", "6", "7"]
precision_partitions = dg.StaticPartitionsDefinition(PRECISION_LEVELS)

def box_hash(hash: str):
    min_lat, min_lon, max_lat, max_lon = pgh.get_bounding_box(hash)
    return box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)

@dg.asset(kinds={"python"}, partitions_def=precision_partitions)
def scored_grids(context: dg.AssetExecutionContext, scored_nodes: pd.DataFrame) -> GeometryCollection:
    """Aggregate scored nodes into grids and average their scores"""

    level = int(context.partition_key)
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
    
    return GeometryCollection(gdf, level)

scored_grids_postgis = geometry_to_postgis_asset(scored_grids.key, partitions_def=precision_partitions)


    