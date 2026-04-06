import osmium
import shapely
import dagster as dg

from typing import cast
from shapely import wkt, LineString
from shapely.geometry.base import BaseGeometry
from shapely.ops import polygonize
from models.models import FileRef
from osmium import filter, osm, geom

@dg.asset(kinds={"python"})
def denmark_coastline(context: dg.AssetExecutionContext, denmark_raw: FileRef) -> list[BaseGeometry]:
    """Create a list of all distinct landmasses in Denmark"""

    file = denmark_raw.path
    fp = osmium.FileProcessor(file) \
        .with_locations() \
        .with_filter(filter.EntityFilter(osm.WAY)) \
        .with_filter(filter.TagFilter(("natural", "coastline")))
    
    fab = geom.WKTFactory()
    ends: dict[tuple[float, float], list[LineString]] = {} # current endpoint -> lines
    starts: dict[tuple[float, float], list[LineString]] = {} # current start -> lines


    way_count = 0
    for way in fp:
        way_count += 1

        way = cast (osm.Way, way)
        line = cast(LineString, wkt.loads(fab.create_linestring(way)))

        (xs, ys) = line.coords.xy
        start = xs[0], ys[0]
        end = xs[len(xs)-1], ys[len(ys)-1]

        acc_end = ends.pop(start, [])
        acc_end.append(line)
        ends[end] = acc_end

        acc_start = starts.pop(end, [])
        acc_start.append(line)
        starts[start] = acc_start

    coastlines: list[BaseGeometry] = []
    for lines in ends.values():
        coastline = shapely.union_all(lines)
        coastlines.append(coastline)

    context.log.info(f"ways found: {way_count}")
    context.log.info(f"coastlines found: {len(coastlines)}")
    return coastlines