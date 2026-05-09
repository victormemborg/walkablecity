import os
import zipfile
import tempfile
import dagster as dg
import httpx
import osmium
import dagster as dg
import geopandas as gpd

from typing import cast
from shapely import wkt
from shapely.geometry.base import BaseGeometry
from shapely.ops import polygonize
from models.models import FileRef
from osmium import filter, osm, geom


URL = "https://osmdata.openstreetmap.de/download/land-polygons-split-4326.zip"
TARGET_FILE = os.path.join("land-polygons-split-4326", "land_polygons.shp")

@dg.asset(kinds={"python"})
async def land_polygons(context: dg.AssetExecutionContext) -> FileRef:
    """Download and extract the worldwide coastline shapefile archive."""
    out_dir = context.instance.storage_directory()

    with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as tmp:
        context.log.info(f"Downloading {URL} to temp file {tmp.name} ...")

        async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
            async with client.stream("GET", URL) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    tmp.write(chunk)
        tmp.flush()

        with zipfile.ZipFile(tmp.name) as zf:
            context.log.info(f"Zip contents: {zf.namelist()}")
            zf.extractall(out_dir)

    # Return a reference to the shapefile witihin the extracted directory
    return FileRef(os.path.join(out_dir, TARGET_FILE))

@dg.asset(kinds={"python"})
def land_polygons_clipped(context: dg.AssetExecutionContext, country_osm: FileRef, land_polygons: FileRef) -> gpd.GeoDataFrame:
    """Create GeoDataFrame of all distinct landmasses witihin country_osm"""

    # Collect way IDs that belong to admin_level=2 boundary relations
    relation_way_ids: set[int] = set()

    file = country_osm.path
    fp_relations = osmium.FileProcessor(file) \
        .with_filter(filter.EntityFilter(osm.RELATION)) \
        .with_filter(filter.TagFilter(("boundary", "administrative"))) \
        .with_filter(filter.TagFilter(("admin_level", "2")))

    for rel in fp_relations:
        rel = cast(osm.Relation, rel)
        for member in rel.members:
            if member.type == "w":  # way member
                relation_way_ids.add(member.ref)

    context.log.info(f"found {len(relation_way_ids)} ways in target relation")

    # Extract those ways as linestrings
    fab = geom.WKTFactory()
    lines: list[BaseGeometry] = []

    fp_ways = osmium.FileProcessor(file) \
        .with_locations() \
        .with_filter(filter.EntityFilter(osm.WAY)) \
        .with_filter(filter.IdFilter(relation_way_ids))

    for way in fp_ways:
        way = cast(osm.Way, way)
        lines.append(wkt.loads(fab.create_linestring(way)))

    context.log.info("finished converting ways to linestrings")

    # Polygonize the linestrings and clip land_polygons to their boundaries
    polygons: list[BaseGeometry] = list(polygonize(lines))
    boundaries = gpd.GeoDataFrame(geometry=polygons, crs=4326)
    landmasses = gpd.read_file(land_polygons.path)[["geometry"]] # keep only the geometry

    clipped = gpd.clip(landmasses, boundaries)
    clipped = clipped.dissolve().explode()

    context.log.info(f"clipped: {clipped.describe()}")
    return clipped
