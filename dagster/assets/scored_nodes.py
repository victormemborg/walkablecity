import dagster as dg
import pandana as pdna
import pandas as pd

@dg.asset(kinds={"python"})
async def denmark_raw(context: dg.AssetExecutionContext, walk_network: pdna.Network, grouped_distances: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Assign an accesibility score to each node in a network"""

    MAX_DIST = 1600 # Meters. Should be passed as run config
    
    dist_df = pd.concat(
        [df["dist"] for df in grouped_distances.values()],
        axis=1
    )

    nodes = walk_network.nodes_df
    nodes["score"] = (dist_df <= MAX_DIST).sum(axis=1)
    scored_nodes = nodes[nodes["score"] > 0]

    context.log.info(f"Found {len(scored_nodes)} scored nodes")
    return scored_nodes

