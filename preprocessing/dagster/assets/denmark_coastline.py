import osmium
import dagster as dg
import geopandas as gpd

from typing import cast
from shapely import wkt
from shapely.geometry.base import BaseGeometry
from shapely.ops import polygonize
from models.models import FileRef
from osmium import filter, osm, geom


@dg.asset(kinds={"python"})
def denmark_coastline(context: dg.AssetExecutionContext, denmark_raw: FileRef) -> gpd.GeoDataFrame:
    """Create a list of all distinct landmasses in Denmark"""

    file = denmark_raw.path
    fp = osmium.FileProcessor(file) \
        .with_locations() \
        .with_filter(filter.EntityFilter(osm.WAY)) \
        .with_filter(filter.TagFilter(("natural", "coastline"), ("boundary", "administrative")))
    
    fab = geom.WKTFactory()
    lines: list[BaseGeometry] = []

    for way in fp:
        way = cast(osm.Way, way)

        tags = way.tags
        if tags.get("boundary") and not tags.get("admin_level") == "2":
            continue
            
        lines.append(wkt.loads(fab.create_linestring(cast(osm.Way, way))))

    polygons: list[BaseGeometry] = list(polygonize(lines))
    gdf = gpd.GeoDataFrame(geometry=polygons, crs=4326).explode()
    context.log.info(f"gdf before: {len(gdf.index)}")

    # Remove maritime boundaries identified by geometry that
    # touches several other geometries 
    self_join = gdf.sjoin(df=gdf, how="inner", predicate="touches")
    touching = self_join.groupby(self_join.index)["index_right"].aggregate(["count"])
    maritime_boundaries = touching[touching["count"] > 1]

    result = gdf.drop(index=maritime_boundaries.index)
    context.log.info(f"gdf after: {len(result)}")
    
    return result