import dagster as dg
import pandas as pd
import pygeohash as pgh
import geopandas as gpd

from shapely.strtree import STRtree
from shapely.geometry import box
from assets.factories.geometry_to_postgis_asset import geometry_to_postgis_asset
from assets.factories.geometry_to_pmtiles_asset import geometry_to_pmtiles_asset
from assets.factories.upload_pmtiles_prod_asset import upload_pmtiles_prod_asset
from collections import deque


PRECISION_LEVELS = ["5", "6", "7"]
precision_partitions = dg.StaticPartitionsDefinition(PRECISION_LEVELS)
BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"

def box_hash(hash: str):
    min_lat, min_lon, max_lat, max_lon = pgh.get_bounding_box(hash)
    return box(minx=min_lon, miny=min_lat, maxx=max_lon, maxy=max_lat)

def get_children(hash: str):
    return [hash + ch for ch in BASE32]

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

    return gpd.GeoDataFrame(data=grouped, geometry="geometry", crs=4326)

@dg.asset(kinds={"python"}, partitions_def=precision_partitions)
def interpolated_grids(
    context: dg.AssetExecutionContext, scored_grids: gpd.GeoDataFrame, land_polygons_clipped: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Let grid cells with no score have score: nearest_scored.score - dist_to(nearest_scored)"""

    level = int(context.partition_key)
    context.log.info(f"Computing geohash precision {level} / {max(PRECISION_LEVELS)} ...")

    tree = STRtree(land_polygons_clipped.geometry)
    hashes = deque(BASE32)
    hashes_on_land: set[str] = set()

    while hashes:
        hash = hashes.popleft()
        cell = box_hash(hash)

        hit = len(tree.query(cell, predicate="intersects")) > 0
        if not hit:
            continue

        if len(hash) == level:
            hashes_on_land.add(hash)
            continue
        
        fully_contained = len(tree.query(cell, predicate="within")) > 0
        if fully_contained:
            children = deque(get_children(hash))

            while children:
                child = children.popleft()

                if len(child) == level:
                    hashes_on_land.add(child)
                    continue

                children.extend(get_children(child))

            continue

        hashes.extend(get_children(hash))

    context.log.info(f"len grids_on_land: {len(hashes_on_land)}")
    non_scored = [box_hash(hash) for hash in hashes_on_land.difference(scored_grids["hash"])]
    non_scored_gdf = gpd.GeoDataFrame(geometry=non_scored, crs=4326)
    context.log.info(f"non_scored_gdf:\n{non_scored_gdf.describe()}")

    non_scored_projected = non_scored_gdf.to_crs(3857)
    scored_projected = scored_grids.to_crs(3857)

    interpolated = non_scored_projected.sjoin_nearest(right=scored_projected, how="inner", distance_col="dist") \
        .groupby(level=0) \
        [["score", "dist"]].mean()

    interpolated = interpolated.join(non_scored_gdf.geometry)
    interpolated["score"] = (interpolated["score"] - interpolated["dist"]).clip(lower=0)
    context.log.info(f"interpolated:\n{interpolated.describe()}")

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

