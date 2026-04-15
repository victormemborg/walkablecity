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

    bounds = landmasses.bounds.iloc[0,:]
    bbox = pgh.BoundingBox(min_lat=bounds["miny"], min_lon=bounds["minx"], max_lat=bounds["maxy"], max_lon=bounds["maxx"])
    hashes_witihin_bounds = pgh.geohashes_in_box(bbox=bbox, precision=level)

    all_grids = [box_hash(hash) for hash in hashes_witihin_bounds]
    context.log.info(f"len all_grids: {len(all_grids)}")
    all_grids_gdf = gpd.GeoDataFrame(geometry=all_grids, crs=4326)
    grids_on_land = all_grids_gdf.sjoin(df=landmasses, how="inner", predicate="intersects")
    context.log.info(grids_on_land.columns)
    context.log.info(grids_on_land.head())
    context.log.info(grids_on_land.describe())
    grids_on_land = grids_on_land[all_grids_gdf.columns] # remove any 'landmasses' columns
    non_scored = grids_on_land.overlay(right=scored_grids, how="difference")

    nearest_scored = non_scored.sjoin_nearest(right=scored_grids, how="inner", distance_col="dist") \
        .groupby("geometry") \
        ["score"].aggregate(["max"]) \
        .reset_index()
    
    nearest_scored = cast(gpd.GeoDataFrame, nearest_scored)
    
    context.log.info(nearest_scored.columns)
    context.log.info(nearest_scored.head())
    context.log.info(nearest_scored.describe())
    nearest_scored["score"] = nearest_scored[nearest_scored["max"] - nearest_scored["dist"]]

    return nearest_scored[scored_grids.columns]

grids_postgis = geometry_to_postgis_asset(interpolated_grids.key, partitions_def=precision_partitions)

grids_pmtiles = geometry_to_pmtiles_asset(interpolated_grids.key, partitions_def=precision_partitions)

grids_uploaded = upload_pmtiles_prod_asset(grids_pmtiles.key, partitions_def=precision_partitions)
    