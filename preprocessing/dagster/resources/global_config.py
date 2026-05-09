from dagster import ConfigurableResource

class GlobalConfig(ConfigurableResource):
    max_distance: int    # meters
    country_url: str # country name -> OSM PBF download URL
