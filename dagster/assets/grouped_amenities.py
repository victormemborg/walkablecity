import dagster as dg
import osmium

from collections import defaultdict
from osmium import filter, osm, geom
from shapely import wkt, Point
from models.models import FileRef

CATEGORY_MAP = {
    # Education
    "school": "education",
    "university": "education",
    # Health
    "hospital": "health",
    "clinic": "health",
    # Grocery
    "supermarket": "grocery",
    "convenience": "grocery",
    # Leisure
    "park": "leisure",
    "playground": "leisure",
    # Culture
    "theatre": "culture",
    "museum": "culture",
}

def group(file_processor):
    """Group osm objects in FileProcessor by category. Objects returned as their centroid."""

    fab = geom.WKTFactory()
    grouped_points: defaultdict[str, list[Point]] = defaultdict(list)

    for osm_obj in file_processor:
        seen_categories = set()

        for tag in osm_obj.tags:
            category = CATEGORY_MAP.get(tag.v)

            if category is None or category in seen_categories:
                continue
            seen_categories.add(category)

            if osm_obj.is_node():
                shape = wkt.loads(fab.create_point(osm_obj))
            elif osm_obj.is_area():
                shape = wkt.loads(fab.create_multipolygon(osm_obj))
            else:
                raise AssertionError(f"Unreachable: {osm_obj}")

            grouped_points[category].append(shape.centroid)
        
    return grouped_points

@dg.asset(kinds={"python"})
def grouped_amenities(context: dg.AssetExecutionContext, denmark_raw: FileRef) -> dict[str, list[Point]]:
    """Group ammenities in the raw PBF data by categories"""

    fp = osmium.FileProcessor(denmark_raw).with_areas() \
        .with_filter(filter.EntityFilter(osm.NODE | osm.AREA))\
        .with_filter(filter.KeyFilter("amenity", "shop", "leisure", "building"))

    grouped_amenities = group(fp)
    for category, amenities in grouped_amenities.items():
        context.log.info(f"Found {len(amenities)} amenities for category {category}")

    return grouped_amenities



