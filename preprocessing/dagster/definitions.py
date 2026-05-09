import dagster as dg

from assets.country_osm import country_osm
from assets.grouped_amenities import grouped_amenities
from assets.grouped_distances import grouped_distances
from assets.edges import scored_edges, edges_postgis, edges_pmtiles, edges_uploaded
from assets.grids import scored_grids, grids_postgis, grids_pmtiles, interpolated_grids, grids_uploaded
from assets.scored_nodes import scored_nodes
from assets.walk_network import walk_network
from assets.land_polygons import land_polygons, land_polygons_clipped

from resources.pandana_network_io_manager import pandana_network_io_manager
from resources.global_config import GlobalConfig
from resources.ssh_resource import ssh_resource

defs = dg.Definitions(
    assets=[
        country_osm, grouped_amenities, grouped_distances, scored_edges,
        scored_edges, scored_grids, scored_nodes, walk_network,
        edges_postgis, edges_pmtiles, grids_postgis, grids_pmtiles, 
        edges_uploaded, grids_uploaded, interpolated_grids, land_polygons,
        land_polygons_clipped
    ],
    resources={
        "pandana_io_manager": pandana_network_io_manager,
        "global_config": GlobalConfig(
        max_distance=100000,
        country_url="https://download.geofabrik.de/europe/denmark-latest.osm.pbf"
    ),
    "ssh": ssh_resource,
    }
)
