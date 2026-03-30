import dagster as dg
from dagster_ssh import SSHResource

ssh_resource = SSHResource(
    remote_host=dg.EnvVar("SERVER_HOST"),
    username=dg.EnvVar("SERVER_USER"),
    remote_port=22,
    key_file="/root/.ssh/dagster_pmtiles",
    no_host_key_check=False,
)