import pandana as pdna
import osmium
from osmium import filter, osm, geom
from shapely import wkt, Point
import geopandas as gpd
import pandas as pd

#################### Collect all amenities ####################

data= "../../denmark-260208.osm.pbf"
fp = osmium.FileProcessor(data).with_areas() \
    .with_filter(filter.EntityFilter(osm.NODE | osm.AREA))\
    .with_filter(filter.KeyFilter("amenity")
)

fab = geom.WKTFactory()

def to_points(fp):
    points: list[Point] = []
    amenities: list[str] = []

    for o in fp:
        if o.is_node():
            shape = wkt.loads(fab.create_point(o))
        elif o.is_area():
            shape = wkt.loads(fab.create_multipolygon(o))
        else:
            raise AssertionError(f"Unreachable: {o}")

        points.append(shape.centroid)
        amenities.append(o.tags.get("amenity"))
        
    return points, amenities

points, amenities = to_points(fp)

#################### Calculate ####################

network = pdna.Network.from_hdf5("denmark.backup")

WALKING_SPEED_KMPH = 4
MAX_WALKING_TIME_MIN = 15
max_distance = WALKING_SPEED_KMPH * 1000 / 60 * MAX_WALKING_TIME_MIN  # meters

category_map = {
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

print("loop begin")
poi_distances = {}
categorised_points

for point, amenity in zip(points, amenities):
    if amenity not in category_map.keys():
        continue

    network.set_pois(
        amenity,
        max_distance,
        1,
        point.x,
        point.y,
    )

    network.nodes_in_range
    
    d = network.nearest_pois(
        max_distance,
        amenity,
        num_pois=1,
        max_distance=max_distance + 1,
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