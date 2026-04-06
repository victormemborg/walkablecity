import osmium
import shapely
import dagster as dg

from typing import cast
from shapely import wkt, LineString
from shapely.geometry.base import BaseGeometry
from shapely.ops import polygonize
from models.models import FileRef
from osmium import filter, osm, geom

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
    starts: dict[point, list[LineString]] = {} # start -> line chain
    ends: dict[point, list[LineString]] = {} # end -> line chain

    for way in fp:
        way = cast (osm.Way, way)
        line = cast(LineString, wkt.loads(fab.create_linestring(way)))

        line_start = getStart(line)
        line_end = getEnd(line)

        chain_end = ends.pop(line_start, [])
        chain_end.append(line)

        chain_start = starts.pop(line_end, None)
        if chain_start is None or chain_end is chain_start:
            ends[line_end] = chain_end
            starts[line_start] = chain_end
            continue

        chain_end.extend(chain_start)
        ends[getEnd(chain_start.pop())] = chain_end
        starts[getStart(chain_end[0])] = chain_end

    coastlines: list[BaseGeometry] = []
    for lines in ends.values():
        coastline = shapely.union_all(lines)
        coastlines.append(coastline)

    context.log.info(f"coastlines found: {len(coastlines)}")
    return coastlines