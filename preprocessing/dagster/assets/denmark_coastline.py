import osmium
import shapely
import dagster as dg

from typing import cast
from shapely import wkt, LineString
from shapely.geometry.base import BaseGeometry
from shapely.ops import polygonize
from models.models import FileRef
from osmium import filter, osm, geom
from collections import deque

point = tuple[float, float]

def getStart(ls: LineString):
    (xs, ys) = ls.coords.xy
    return xs[0], ys[0]

def getEnd(ls: LineString):
    (xs, ys) = ls.coords.xy
    return xs[len(xs)-1], ys[len(ys)-1]

@dg.asset(kinds={"python"})
def denmark_coastline(context: dg.AssetExecutionContext, denmark_raw: FileRef) -> list[BaseGeometry]:
    """Create a list of all distinct landmasses in Denmark"""

    file = denmark_raw.path
    fp = osmium.FileProcessor(file) \
        .with_locations() \
        .with_filter(filter.EntityFilter(osm.WAY)) \
        .with_filter(filter.TagFilter(("natural", "coastline")))
    
    fab = geom.WKTFactory()

    starts: dict[point, deque[LineString]] = {} # current start -> lines, current end
    ends: dict[point, deque[LineString]] = {} # current endpoint -> lines, current start

    way_count = 0
    for way in fp:
        way_count += 1

        way = cast (osm.Way, way)
        line = cast(LineString, wkt.loads(fab.create_linestring(way)))

        line_start = getStart(line)
        line_end = getEnd(line)

        chain1 = ends.pop(line_start, deque([]))
        chain1.append(line)

        chain2 = starts.pop(line_end, None)
        if chain2 is None:
            ends[line_end] = chain1
            starts[line_start] = chain1
            continue
        
        if chain1 is chain2:
            ends[line_end] = chain1
            starts[line_start] = chain1
            continue

        chain1.extend(chain2)
        ends[getEnd(chain2.pop())] = chain1
        starts[getStart(chain1[0])] = chain1

    coastlines: list[BaseGeometry] = []
    for lines in ends.values():
        coastline = shapely.union_all(lines)
        coastlines.append(coastline)

    context.log.info(f"ways found: {way_count}")
    context.log.info(f"coastlines found: {len(coastlines)}")
    return coastlines