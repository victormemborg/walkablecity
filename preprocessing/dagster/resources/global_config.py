from dagster import ConfigurableResource

class GlobalConfig(ConfigurableResource):
    max_distance: int    # meters
