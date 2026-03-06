import dagster as dg

from assets.denmark_raw import denmark_raw
from assets.grouped_amenities import grouped_amenities
from assets.grouped_distances import grouped_distances
from assets.scored_edges import scored_edges
from assets.scored_grids import scored_grids
from assets.scored_nodes import scored_nodes
from assets.stored_edges import stored_edges
from assets.stored_grids import stored_grids
from assets.walk_network import walk_network

defs = dg.Definitions(
    assets=[
        denmark_raw, grouped_amenities, grouped_distances, scored_edges,
        scored_edges, scored_grids, scored_nodes, stored_edges,
        stored_grids, walk_network,
    ],
)