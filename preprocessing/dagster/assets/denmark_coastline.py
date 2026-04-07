import osmium
import dagster as dg

from typing import cast
from shapely import wkt
from shapely.geometry.base import BaseGeometry
from shapely.ops import polygonize
from models.models import FileRef
from osmium import filter, osm, geom


@dg.asset(kinds={"python"})
async def denmark_coastline(context: dg.AssetExecutionContext, denmark_raw: FileRef) -> list[BaseGeometry]:
    """Create a list of all distinct landmasses in Denmark"""

    file = denmark_raw.path
    fp = osmium.FileProcessor(file) \
        .with_locations() \
        .with_filter(filter.EntityFilter(osm.WAY)) \
        .with_filter(filter.TagFilter(("natural", "coastline"), ("boundary", "administrative")))
    
    fab = geom.WKTFactory()
    lines: list[BaseGeometry] = []

    #1065
    for way in fp:
        way = cast(osm.Way, way)

        tags = way.tags
        if tags.get("boundary") and not tags.get("admin_level") == "2":
            continue

        lines.append(wkt.loads(fab.create_linestring(cast(osm.Way, way))) )

    polygons: list[BaseGeometry] = list(polygonize(lines))

    context.log.info(f"coastlines found: {len(polygons)}")
    return polygons