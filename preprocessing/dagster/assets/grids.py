import dagster as dg
import pandas as pd
import pygeohash as pgh
import geopandas as gpd

from shapely.geometry import box
from assets.factories.geometry_to_postgis_asset import geometry_to_postgis_asset
from assets.factories.geometry_to_pmtiles_asset import geometry_to_pmtiles_asset


PRECISION_LEVELS = ["5", "6", "7"]
precision_partitions = dg.StaticPartitionsDefinition(PRECISION_LEVELS)

def box_hash(hash: str):
    min_lat, min_lon, max_lat, max_lon = pgh.get_bounding_box(hash)
    return box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)

@dg.asset(kinds={"python"}, partitions_def=precision_partitions)
def scored_grids(context: dg.AssetExecutionContext, scored_nodes: pd.DataFrame) -> gpd.GeoDataFrame:
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
    return gpd.GeoDataFrame(final, geometry="geometry", crs=4326)

@dg.asset(kinds={"python"}, partitions_def=precision_partitions)
def interpolated_grids(context: dg.AssetExecutionContext, scored_grids: gpd.GeoDataFrame):
    """If any non-scored grid cell has X neighboring scored cells, assume score to be average of neighbors"""

    level = int(context.partition_key)
    context.log.info(f"Computing geohash precision {level} / {max(PRECISION_LEVELS)} ...")

    count = scored_grids.sjoin(df=scored_grids, how="left", predicate="touches").groupby(level=0).size().rename("neighbor_count")
    neighbors = scored_grids.join(count)
    print(f"before: {len(scored_grids.index)}, after: {len(neighbors.index)}")
    print(neighbors.head())
    print(neighbors.describe())
    """
    for geometry in scored_grids.geometry:
        grid = pgh.encode(latitude=geometry.centroid.x, longitude=geometry.centroid.y, precision=level)
        sum_sorrounding = 0

        

        right = pgh.get_adjacent(grid, "right")
        if scored_grids.

        left = pgh.get_adjacent(grid, "left")
        top = pgh.get_adjacent(grid, "top")
        bottom = pgh.get_adjacent(grid, "bottom")
    """
    return neighbors

scored_grids_postgis = geometry_to_postgis_asset(interpolated_grids.key, partitions_def=precision_partitions)

scored_grids_pmtiles = geometry_to_pmtiles_asset(interpolated_grids.key, partitions_def=precision_partitions)


    