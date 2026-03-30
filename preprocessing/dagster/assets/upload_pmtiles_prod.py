from assets.edges import scored_edges_pmtiles
from assets.factories.upload_pmtiles_prod_asset import upload_pmtiles_prod_asset
from assets.grids import precision_partitions, scored_grids_pmtiles


upload_scored_edges_pmtiles_prod = upload_pmtiles_prod_asset(scored_edges_pmtiles.key)
upload_scored_grids_pmtiles_prod = upload_pmtiles_prod_asset(
    scored_grids_pmtiles.key,
    partitions_def=precision_partitions
)
