import dagster as dg
import pandana as pdna
import pandas as pd

from resources.global_config import GlobalConfig

@dg.asset(kinds={"python"})
async def scored_nodes(
    context: dg.AssetExecutionContext, 
    walk_network: pdna.Network, 
    grouped_distances: dict[str, pd.DataFrame], 
    global_config: GlobalConfig
) -> pd.DataFrame:
    """Assign an accesibility score to each node in a network"""
    
    dist_df = pd.concat(
        [df["dist"] for df in grouped_distances.values()],
        axis=1
    )

    nodes = walk_network.nodes_df
    nodes["score"] = dist_df.max(axis="columns")
    nodes["score"] = nodes["score"].apply(lambda dist: abs(dist - global_config.max_distance))
    scored = nodes[nodes["score"] <= global_config.max_distance]

    context.log.info(f"Found {len(scored)} scored nodes")
    return scored

