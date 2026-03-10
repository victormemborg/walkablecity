import os
from dagster import IOManager, io_manager, InputContext, OutputContext
import pandana as pdna


class PandanaNetworkIOManager(IOManager):
    """Custom IO manager for pandana Network objects using HDF5 storage."""

    def __init__(self, base_dir: str = "/tmp/dagster_pandana"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def _get_path(self, context) -> str:
        parts = context.asset_key.path if context.has_asset_key else [context.step_key, context.name]
        filename = "__".join(parts) + ".h5"
        return os.path.join(self.base_dir, filename)

    def handle_output(self, context: OutputContext, obj: pdna.Network):
        path = self._get_path(context)
        context.log.info(f"Saving pandana Network to {path}")
        obj.save_hdf5(path)

    def load_input(self, context: InputContext) -> pdna.Network:
        path = self._get_path(context.upstream_output)
        context.log.info(f"Loading pandana Network from {path}")
        return pdna.Network.from_hdf5(path)


@io_manager(config_schema={"base_dir": str})
def pandana_network_io_manager(context):
    return PandanaNetworkIOManager(
        base_dir=context.resource_config.get("base_dir", "/tmp/dagster_pandana")
    )