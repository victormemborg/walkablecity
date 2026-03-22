import dagster as dg
import pandana as pdna
import pandas as pd

from shapely import Point
from resources.global_config import GlobalConfig

@dg.asset(kinds={"python"})
def grouped_distances(
    context: dg.AssetExecutionContext,
    walk_network: pdna.Network, 
    grouped_amenities: dict[str, list[Point]],
    global_config: GlobalConfig
) -> dict[str, pd.DataFrame]:
    """Calculates the distances to each amenity group/category for every node in a network"""

    grouped_distances: dict[str, pd.DataFrame] = {}

    for category, amenities in grouped_amenities.items():
        context.log.info(f"Computing category: {category}")

        walk_network.set_pois(
            category=category,
            maxdist=global_config.max_distance,
            maxitems=1,
            x_col=[amenity.x for amenity in amenities],
            y_col=[amenity.y for amenity in amenities],
        )
        
        nearest = walk_network.nearest_pois(
            distance=global_config.max_distance,
            category=category,
            num_pois=1,
            max_distance=global_config.max_distance + 1,
        )

        nearest.columns = ["dist"]
        grouped_distances[category] = nearest

    return grouped_distances

