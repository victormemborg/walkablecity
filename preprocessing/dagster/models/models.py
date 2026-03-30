from dataclasses import dataclass
from pathlib import Path

@dataclass
class FileRef():
    path: str

    @property
    def name(self) -> str:
        return Path(self.path).name

@dataclass
class PostGISTable():
    table_name: str
    connection_str: str
    shchema: str

@dataclass
class SSHConfig():
    host: str
    user: str
    remote_dir: str
