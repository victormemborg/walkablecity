import dagster as dg
import pandas as pd
import pygeohash as pgh
import geopandas as gpd

from shapely.geometry import box, Polygon
from shapely.geometry.base import BaseGeometry
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
    """If any non-scored grid cell has 8 neighboring scored cells, assume score to be average of neighbors"""

    level = int(context.partition_key)
    context.log.info(f"Computing geohash precision {level} / {max(PRECISION_LEVELS)} ...")

    already_scored: set[BaseGeometry] = set(scored_grids.geometry)
    eligable_grids: set[BaseGeometry] = set() # Grids to be considered for interpolation

    for scored_grid in scored_grids.geometry:
        scored_hash = pgh.encode(latitude=scored_grid.centroid.y, longitude=scored_grid.centroid.x, precision=level)
        directions: list[pgh.Direction] = ["left", "right", "top", "bottom"]

        for direction in directions:
            adjacent_hash = pgh.get_adjacent(scored_hash, direction)
            adjacent_grid = box_hash(adjacent_hash)

            if not adjacent_grid in already_scored:
                eligable_grids.add(adjacent_grid)

    eligable = gpd.GeoDataFrame(geometry=list(eligable_grids), crs=4326)
    count = eligable.sjoin(df=scored_grids, how="left", predicate="touches") \
        .groupby(level=0) \
        .size() \
        .rename("neighbor_count")
    
    neighbors = eligable.join(count)
    print(neighbors.head())
    print(neighbors.describe())

    return neighbors

scored_grids_postgis = geometry_to_postgis_asset(interpolated_grids.key, partitions_def=precision_partitions)

scored_grids_pmtiles = geometry_to_pmtiles_asset(interpolated_grids.key, partitions_def=precision_partitions)


    