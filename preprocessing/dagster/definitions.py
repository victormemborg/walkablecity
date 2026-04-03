import dagster as dg

from assets.denmark_raw import denmark_raw
from assets.grouped_amenities import grouped_amenities
from assets.grouped_distances import grouped_distances
from assets.edges import scored_edges, scored_edges_postgis, scored_edges_pmtiles
from assets.grids import scored_grids, scored_grids_postgis, scored_grids_pmtiles, interpolated_grids
from assets.scored_nodes import scored_nodes
from assets.upload_pmtiles_prod import upload_scored_edges_pmtiles_prod, upload_scored_grids_pmtiles_prod
from assets.walk_network import walk_network

from resources.pandana_network_io_manager import pandana_network_io_manager
from resources.global_config import GlobalConfig
from resources.ssh_resource import ssh_resource

defs = dg.Definitions(
    assets=[
        denmark_raw, grouped_amenities, grouped_distances, scored_edges,
        scored_edges, scored_grids, scored_nodes, walk_network,
        scored_edges_postgis, scored_edges_pmtiles, scored_grids_postgis,
        scored_grids_pmtiles, upload_scored_edges_pmtiles_prod,
        upload_scored_grids_pmtiles_prod, interpolated_grids
    ],
    resources={
        "pandana_io_manager": pandana_network_io_manager,
        "global_config": GlobalConfig(max_distance=10000),
        "ssh": ssh_resource,
    }
)
