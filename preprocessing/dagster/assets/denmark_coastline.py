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

@dg.asset(kinds={"python"})
def denmark_coastline(context: dg.AssetExecutionContext, denmark_raw: FileRef) -> list[BaseGeometry]:
    """Create a list of all distinct landmasses in Denmark"""

    file = denmark_raw.path
    fp = osmium.FileProcessor(file) \
        .with_locations() \
        .with_filter(filter.EntityFilter(osm.WAY)) \
        .with_filter(filter.TagFilter(("natural", "coastline")))
    
    fab = geom.WKTFactory()

    ends: dict[point, tuple[list[LineString], point]] = {} # current endpoint -> lines, current start
    starts: dict[point, tuple[list[LineString], point]] = {} # current start -> lines, current end


    way_count = 0
    for way in fp:
        way_count += 1

        way = cast (osm.Way, way)
        line = cast(LineString, wkt.loads(fab.create_linestring(way)))

        (xs, ys) = line.coords.xy
        line_start = xs[0], ys[0]
        line_end = xs[len(xs)-1], ys[len(ys)-1]

        (acc1, start) = ends.pop(line_start, ([], line_start))
        acc1.append(line)

        (acc2, end) = starts.pop(line_end, ([], line_end))
        acc1.extend(starts.pop(line_end, []))

        ends[line_end] = acc1.copy()
        starts[line_start] = acc1.copy()

#    coastlines: list[BaseGeometry] = []
#    for lines in ends.values():
#        print()
#        coastline = shapely.union_all(lines)
#        coastlines.append(coastline)
#
    coastlines = list(*ends.values())

    context.log.info(f"ways found: {way_count}")
    context.log.info(f"coastlines found: {len(coastlines)}")
    return coastlines