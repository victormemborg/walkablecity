import dagster as dg
import pandana as pdna
import pandas as pd

from resources.global_config import GlobalConfig

@dg.asset(kinds={"python"})
def scored_nodes(
    context: dg.AssetExecutionContext, 
    walk_network: pdna.Network, 
    grouped_distances: dict[str, pd.DataFrame], 
    global_config: GlobalConfig
) -> pd.DataFrame:
    """Assign an accesibility score to each node in a network"""
    
    dist_df = pd.concat(
        [df["dist"] for df in grouped_distances.values()],
        axis="columns"
    )

    nodes = walk_network.nodes_df
    nodes["dist"] = dist_df.max(axis="columns")

    filtered = nodes[nodes["dist"] <= global_config.max_distance]
    max_found_dist = filtered["dist"].max() # With current categories its 45898.8515625 (meters)
    context.log.info(f"max found dist: {max_found_dist}")

    filtered["score"] = abs(filtered["dist"] - max_found_dist)
    filtered.drop(columns=["dist"])

    context.log.info(f"Found {len(filtered)} scored nodes")
    return filtered

