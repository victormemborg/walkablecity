import pandana as pdna
import osmium
from osmium import filter, osm, geom
from shapely import wkt, Point
import pandas as pd
from collections import defaultdict
import pickle

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
    .with_filter(filter.KeyFilter("amenity", "shop", "leisure", "building"))

def categorize(fp):
    fab = geom.WKTFactory()
    categorized_points: defaultdict[str, list[Point]] = defaultdict(list)

    for o in fp:
        seen_categories = set()

        for tag in o.tags:
            category = CATEGORY_MAP.get(tag.v)

            if category is None or category in seen_categories:
                continue
            seen_categories.add(category)

            if o.is_node():
                shape = wkt.loads(fab.create_point(o))
            elif o.is_area():
                shape = wkt.loads(fab.create_multipolygon(o))
            else:
                raise AssertionError(f"Unreachable: {o}")

            categorized_points[category].append(shape.centroid)
        
    return categorized_points

categorized_points = categorize(fp)

print("Found the following number of categories:")
for cat, ps in categorized_points.items():
    print(f"{cat}: {len(ps)}")

#################### Calculate ####################

network = pdna.Network.from_hdf5("denmark.backup")

max_dist = 1600 #meters
nearest_categories: dict[str, pd.DataFrame] = {}

for category, points in categorized_points.items():
    print(f"Computing category: {category}")

    network.set_pois(
        category=category,
        maxdist=max_dist,
        maxitems=1,
        x_col=[p.x for p in points],
        y_col=[p.y for p in points],
    )
    
    nearest = network.nearest_pois(
        distance=max_dist,
        category=category,
        num_pois=1,
        max_distance=max_dist + 1,
    )
    
    nearest_categories[category] = nearest

print("Writing results to disk")
with open("nearest_categories.pkl", "wb") as f:
    pickle.dump(nearest_categories, f)