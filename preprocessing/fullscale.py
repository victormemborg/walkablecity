import pandana as pdna
import osmium
from osmium import filter, osm, geom
from shapely import wkt
import geopandas as gpd
import pandas as pd

#################### Collect all amenities ####################

data= "../../denmark-260208.osm.pbf"
fp = osmium.FileProcessor(data).with_areas() \
    .with_filter(filter.EntityFilter(osm.NODE | osm.AREA))\
    .with_filter(filter.KeyFilter("amenity")
)

fab = geom.WKTFactory()

def to_points(o):
    if o.is_node():
        point = wkt.loads(fab.create_point(o))
    elif o.is_area():
        poly = wkt.loads(fab.create_multipolygon(o))
        point = poly.centroid
    else:
        raise AssertionError(f"Unreachable: {o}")

    return point, o.tags.get("amenity")

points, names = map(list, zip(*[to_points(obj) for obj in fp]))

gdf = gpd.GeoDataFrame(
    {"amenity": names},
    geometry=points,
    crs="EPSG:4326"
)

#################### Calculate ####################

network = pdna.Network.from_hdf5("denmark.backup")

WALKING_SPEED_KMPH = 4
MAX_WALKING_TIME_MIN = 15
max_distance = WALKING_SPEED_KMPH * 1000 / 60 * MAX_WALKING_TIME_MIN  # meters

print("precumputing begin")
network.precompute(max_distance)
print("precumputing end")

categories = {
    "education": {"amenity": ["school", "university"]},
    "health": {"amenity": ["hospital", "clinic"]},
    "grocery": {"shop": ["supermarket", "convenience"]},
    "leisure": {"leisure": ["park", "playground"]},
    "culture": {"amenity": ["theatre", "museum"]},
}

print("loop begin")
poi_distances = {}

for point, name in zip(points, names):
    if name not in categories.items():
        continue

    network.set_pois(
        name,
        max_distance,
        1,
        point.x,
        point.y,
    )
    
    d = network.nearest_pois(
        max_distance,
        name,
        num_pois=1,
        max_distance=max_distance + 1,
    ).iloc[:, 0]
    
    poi_distances[name] = d

print("loop end")
poi_distances = pd.DataFrame(poi_distances)

print("pandas begin")
# Binary reachability per category (1 if reachable within 15 min, else 0)
poi_distances = poi_distances.reindex(columns=categories.keys())
reachable = (poi_distances <= max_distance).fillna(False).astype(int)
access_score = reachable.sum(axis=1)
print("pandas end")

print(access_score.describe())