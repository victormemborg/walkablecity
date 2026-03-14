import dagster as dg
import pandana as pdna
import pandas as pd

from shapely import Point

@dg.asset(kinds={"python"})
def grouped_distances(context: dg.AssetExecutionContext, walk_network: pdna.Network, grouped_amenities: dict[str, list[Point]]) -> dict[str, pd.DataFrame]:
    """Calculates the distances to each amenity group/category for every node in a network"""

    MAX_DIST = 1600 # Meters. Should be passed as run config
    grouped_distances: dict[str, pd.DataFrame] = {}

    for category, amenities in grouped_amenities.items():
        context.log.info(f"Computing category: {category}")

        walk_network.set_pois(
            category=category,
            maxdist=MAX_DIST,
            maxitems=1,
            x_col=[amenity.x for amenity in amenities],
            y_col=[amenity.y for amenity in amenities],
        )
        
        nearest = walk_network.nearest_pois(
            distance=MAX_DIST,
            category=category,
            num_pois=1,
            max_distance=MAX_DIST + 1,
        )

        nearest.columns = ["dist"]
        grouped_distances[category] = nearest

    return grouped_distances

