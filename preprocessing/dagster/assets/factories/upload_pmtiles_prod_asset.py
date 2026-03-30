import os
from dagster import AssetExecutionContext, AssetIn, AssetKey, asset

from models.models import FileRef, SSHConfig

def upload_pmtiles_prod_asset(upstream: AssetKey, partitions_def=None):
    """Returns a new asset that uploads syncs pmtiles to production."""
    upstream_name = upstream.path[-1]
    asset_name = f"upload_{upstream_name}_prod"

    @asset(
        name=asset_name,
        ins={"pmtiles": AssetIn(key=upstream)},
        partitions_def=partitions_def,
        kinds={"python"},
        required_resource_keys={"ssh"},
    )
    def upload_pmtiles(context: AssetExecutionContext, pmtiles: FileRef) -> FileRef:
        ssh = context.resources.ssh
        ssh_config = SSHConfig(
            host=os.environ["SERVER_HOST"],
            user=os.environ["SERVER_USER"],
            remote_dir=f"/home/{os.environ['SERVER_USER']}/bachelor-thesis/tiles",
        )
        
        remote_path = f"{ssh_config.remote_dir}/{pmtiles.name}"

        context.log.info(f"Ensuring remote directory exists: {ssh_config.remote_dir}")
        with ssh.get_connection() as ssh_client:
            _, stdout, _ = ssh_client.exec_command(f"mkdir -p {ssh_config.remote_dir}")
            exit_code = stdout.channel.recv_exit_status()

            if exit_code != 0:
                raise RuntimeError(f"SSH command failed. exit code: {exit_code}")

        context.log.info(f"Uploading {pmtiles.path} to {remote_path}")
        ssh.sftp_put(remote_path, pmtiles.path)

        context.add_output_metadata({
            "remote_path": remote_path,
            "remote_host": ssh_config.host,
        })

        return FileRef(remote_path)

    return upload_pmtiles
