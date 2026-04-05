import dagster as dg
import pandana as pdna
import pandas as pd
import geopandas as gpd

from shapely.geometry import LineString
from assets.factories.geometry_to_postgis_asset import geometry_to_postgis_asset
from assets.factories.geometry_to_pmtiles_asset import geometry_to_pmtiles_asset
from assets.factories.upload_pmtiles_prod_asset import upload_pmtiles_prod_asset

@dg.asset(kinds={"python"})
def scored_edges(context: dg.AssetExecutionContext, walk_network: pdna.Network, scored_nodes: pd.DataFrame) -> gpd.GeoDataFrame:
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

    return gpd.GeoDataFrame(edges, geometry="geometry", crs=4326)

edges_postgis = geometry_to_postgis_asset(scored_edges.key)

edges_pmtiles = geometry_to_pmtiles_asset(scored_edges.key)

edges_uploaded = upload_pmtiles_prod_asset(edges_pmtiles.key)
