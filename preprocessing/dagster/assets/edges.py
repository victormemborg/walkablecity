import dagster as dg
import pandana as pdna
import pandas as pd
import geopandas as gpd

from shapely.geometry import LineString
from models.models import GeometryCollection
from assets.factories.geometry_to_postgis_table import geometry_to_postgis_asset

@dg.asset(kinds={"python"})
async def scored_edges(context: dg.AssetExecutionContext, walk_network: pdna.Network, scored_nodes: pd.DataFrame) -> GeometryCollection:
    """Assign an accesibility score to each edge"""

    edges = walk_network.edges_df.merge(
        scored_nodes[["x", "y", "score"]],
        left_on="from",
        right_index=True,
    ).rename(columns={"x": "x_from", "y": "y_from", "score": "score_from"})

    edges = edges.merge(
        scored_nodes[["x", "y", "score"]],
        left_on="to",
        right_index=True,
    ).rename(columns={"x": "x_to", "y": "y_to", "score": "score_to"})

    edges["geometry"] = edges.apply(
        lambda row: LineString([
            (row["x_from"], row["y_from"]),
            (row["x_to"], row["y_to"]),
        ]),
        axis=1
    )

    edges["score"] = edges.apply(
        lambda row: (row["score_from"] + row["score_to"]) / 2,
        axis=1
    )

    edges = edges[["geometry", "score"]]
    edges = edges[edges["score"] > 0]

    gdf = gpd.GeoDataFrame(edges, geometry="geometry", crs=4326)
    return GeometryCollection(gdf, 0)

scored_edges_postgis = geometry_to_postgis_asset(scored_edges.key)