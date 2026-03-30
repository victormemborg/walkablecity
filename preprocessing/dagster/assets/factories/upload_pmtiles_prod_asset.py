import os
import subprocess
from pathlib import Path

from dagster import AssetExecutionContext, AssetIn, AssetKey, asset

from models.models import FileRef


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
        server_host = os.environ["SERVER_HOST"]
        server_user = os.environ["SERVER_USER"]
        remote_dir = f"/home/{server_user}/bachelor-thesis/tiles"
        remote_path = f"{remote_dir}/{os.path.basename(pmtiles.path)}"

        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(parents=True, exist_ok=True)

        known_hosts = ssh_dir / "known_hosts"
        with known_hosts.open("a", encoding="utf-8") as known_hosts_file:
            subprocess.run(
                ["ssh-keyscan", "-H", server_host],
                check=True,
                stdout=known_hosts_file,
            )

        ssh = context.resources.ssh

        context.log.info(f"Ensuring remote directory exists: {remote_dir}")
        with ssh.get_connection() as ssh_client:
            _, stdout, _ = ssh_client.exec_command(f"mkdir -p {remote_dir}")
            exit_code = stdout.channel.recv_exit_status()

            if exit_code != 0:
                raise RuntimeError(f"SSH command failed. exit code: {exit_code}")

        context.log.info(f"Uploading {pmtiles.path} to {remote_path}")
        ssh.sftp_put(remote_path, pmtiles.path)

        context.add_output_metadata({
            "remote_path": remote_path,
            "remote_host": server_host,
        })

        return FileRef(remote_path)

    return upload_pmtiles