import dagster as dg
import pandas as pd
import pygeohash as pgh
import geopandas as gpd

from typing import cast
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry
from assets.factories.geometry_to_postgis_asset import geometry_to_postgis_asset
from assets.factories.geometry_to_pmtiles_asset import geometry_to_pmtiles_asset
from assets.factories.upload_pmtiles_prod_asset import upload_pmtiles_prod_asset


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

    level_df = scored_nodes[["score"]]
    level_df["hash"] = hashes

    grouped = level_df.groupby("hash", as_index=False).agg({"score": "mean"})
    grouped["geometry"] = grouped["hash"].map(box_hash)

    final = grouped[["geometry", "score"]]
    return gpd.GeoDataFrame(data=final, geometry="geometry", crs=4326)

@dg.asset(kinds={"python"}, partitions_def=precision_partitions)
def interpolated_grids(context: dg.AssetExecutionContext, scored_grids: gpd.GeoDataFrame, landmasses: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Let grid cells with no score have score: nearest_scored.score - dist_to(nearest_scored)"""

    level = int(context.partition_key)
    context.log.info(f"Computing geohash precision {level} / {max(PRECISION_LEVELS)} ...")

    (minx, miny, maxx, maxy) = landmasses.total_bounds
    bbox = pgh.BoundingBox(min_lat=miny, min_lon=minx, max_lat=maxy, max_lon=maxx)
    hashes_witihin_bounds = pgh.geohashes_in_box(bbox=bbox, precision=level)

    all_grids = [box_hash(hash) for hash in hashes_witihin_bounds]
    all_grids_gdf = gpd.GeoDataFrame(geometry=all_grids, crs=4326)
    context.log.info(f"len all_grids: {len(all_grids)}")

    grids_on_land = all_grids_gdf.sjoin(df=landmasses, how="inner", predicate="intersects")
    grids_on_land = grids_on_land.drop_duplicates(subset="geometry")
    grids_on_land = grids_on_land[all_grids_gdf.columns] # Remove 'landmasses' columns
    context.log.info(f"len grids_on_land: {len(grids_on_land.index)}")

    non_scored_grids = grids_on_land.overlay(right=scored_grids, how="difference")
    non_scored_projected = non_scored_grids.to_crs(3857)
    scored_projected = scored_grids.to_crs(3857)

    interpolated = non_scored_projected.sjoin_nearest(right=scored_projected, how="inner", distance_col="dist") \
        .groupby(level=0) \
        [["score", "dist"]].mean()

    interpolated = interpolated.join(non_scored_grids.geometry)
    interpolated["score"] = (interpolated["score"] - interpolated["dist"]).clip(lower=0)
    context.log.info(interpolated.describe())

    columns = ["geometry", "score"]
    merged = gpd.GeoDataFrame(
        data=pd.concat([interpolated[columns], scored_grids[columns]], ignore_index=True),
        geometry="geometry",
        crs=4326
    )

    return merged

grids_postgis = geometry_to_postgis_asset(interpolated_grids.key, partitions_def=precision_partitions)

grids_pmtiles = geometry_to_pmtiles_asset(interpolated_grids.key, partitions_def=precision_partitions)

grids_uploaded = upload_pmtiles_prod_asset(grids_pmtiles.key, partitions_def=precision_partitions)

#                 max
# count   1203.000000
# mean   33169.200531
# std     8213.058506
# min     7679.128795
# 25%    30146.801683
# 50%    35457.595825
# 75%    38589.745934
# max    44868.761543
    