import pandana as pdna
import osmium
from osmium import filter, osm, geom
from shapely import wkt, Point
import geopandas as gpd
import pandas as pd
from collections import defaultdict

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

#################### Collect all amenities ####################

data= "../../denmark-260208.osm.pbf"
fp = osmium.FileProcessor(data).with_areas() \
    .with_filter(filter.EntityFilter(osm.NODE | osm.AREA))\
    .with_filter(filter.KeyFilter("amenity")
)

def categorize(fp):
    fab = geom.WKTFactory()
    categorized_points: defaultdict[str, list[Point]] = defaultdict(list)

    for o in fp:
        amenity = o.tags.get("amenity")
        category = CATEGORY_MAP.get(amenity)
        if category is None:
            continue

        if o.is_node():
            shape = wkt.loads(fab.create_point(o))
        elif o.is_area():
            shape = wkt.loads(fab.create_multipolygon(o))
        else:
            raise AssertionError(f"Unreachable: {o}")

        categorized_points[category].append(shape.centroid)
        
    return categorized_points

categorized_points = categorize(fp)

#################### Calculate ####################

network = pdna.Network.from_hdf5("denmark.backup")

WALKING_SPEED_KMPH = 4
MAX_WALKING_TIME_MIN = 15
max_dist = WALKING_SPEED_KMPH * 1000 / 60 * MAX_WALKING_TIME_MIN  # meters

print("loop begin")
poi_distances = {}

for category, points in categorized_points.items():
    network.set_pois(
        category=category,
        maxdist=max_dist,
        maxitems=1,
        x_col=[p.x for p in points],
        y_col=[p.y for p in points],
    )
    
    d = network.nearest_pois(
        distance=max_dist,
        category=category,
        num_pois=1,
        max_distance=max_dist + 1,
    ).iloc[:, 0]
    
    poi_distances[amenity] = d

print("loop end")
poi_distances = pd.DataFrame(poi_distances)

print("pandas begin")
# Binary reachability per category (1 if reachable within 15 min, else 0)
poi_distances = poi_distances.reindex(columns=categories.keys())
reachable = (poi_distances <= max_distance).fillna(False).astype(int)
access_score = reachable.sum(axis=1)
print("pandas end")

print(access_score.describe())