import dagster as dg

from assets.denmark_raw import denmark_raw
from assets.grouped_amenities import grouped_amenities
from assets.grouped_distances import grouped_distances
from assets.edges import scored_edges, scored_edges_postgis
from assets.grids import scored_grids
from assets.scored_nodes import scored_nodes
from assets.walk_network import walk_network

from resources.pandana_network_io_manager import pandana_network_io_manager

defs = dg.Definitions(
    assets=[
        denmark_raw, grouped_amenities, grouped_distances, scored_edges,
        scored_edges, scored_grids, scored_nodes, walk_network, 
        scored_edges_postgis
    ],
    resources={
        "pandana_io_manager": pandana_network_io_manager
    }
)