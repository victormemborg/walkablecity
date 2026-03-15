import geopandas as gpd

from dataclasses import dataclass

@dataclass
class FileRef():
    path: str

@dataclass
class GeometryCollection():
    geometry: gpd.GeoDataFrame
    precision_level: int

@dataclass
class PostGISTable():
    table_name: str
    connection_str: str
    shchema: str