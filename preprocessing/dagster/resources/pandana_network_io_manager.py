import os
from dagster import IOManager, io_manager, InputContext, OutputContext
import pandana as pdna


class PandanaNetworkIOManager(IOManager):
    """Custom IO manager for pandana Network objects using HDF5 storage."""

    def _get_path(self, context) -> str:
        base_dir = os.path.join(context.instance.storage_directory(), "storage")

        if context.has_asset_key:
            return os.path.join(base_dir, *context.asset_key.path)

        return os.path.join(
            base_dir,
            context.step_key,
            context.name,
        )

    def handle_output(self, context: OutputContext, obj: pdna.Network):
        path = self._get_path(context)
        context.log.info(f"Saving pandana Network to {path}")
        obj.save_hdf5(path)

    def load_input(self, context: InputContext) -> pdna.Network:
        path = self._get_path(context.upstream_output)
        context.log.info(f"Loading pandana Network from {path}")
        return pdna.Network.from_hdf5(path)


@io_manager()
def pandana_network_io_manager():
    return PandanaNetworkIOManager()