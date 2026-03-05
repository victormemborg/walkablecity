# https://docs.osmcode.org/pyosmium/latest/user_manual/04-Working-with-Filters/

import dagster as dg
import osmium
import numpy as np
import pandas as pd
import pandana as pdna

from pathlib import Path
from osmium import filter, osm
from models.models import WalkNetwork, RawPBF

DATA_DIR = Path("../data")
DATA_DIR.mkdir(exist_ok=True)

def haversine_np(n1, n2):
    R = 6371000  # Earth radius in meters

    lat1 = np.radians(n1.lat)
    lon1 = np.radians(n1.lon)
    lat2 = np.radians(n2.lat)
    lon2 = np.radians(n2.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c

@dg.asset(kinds={"python"})
async def walk_network(context: dg.AssetExecutionContext, denmark_raw: RawPBF) -> WalkNetwork:
    """Create Pandana network from the raw data"""

    out_path = DATA_DIR / "walk-network.hdf5"
    if out_path.exists():
        context.log.info(f"{out_path} already exists. Reusing asset...")
        return WalkNetwork(out_path)
    
    context.log.info(f"Parsing {denmark_raw}...")

    fp = osmium.FileProcessor(denmark_raw) \
        .with_locations() \
        .with_filter(filter.EntityFilter(osm.WAY)) \
        .with_filter(filter.KeyFilter("highway"))

    node_dict = {}  # node_id -> node
    edges_list = []  # tuples of (from_id, to_id, dist)

    for way in fp:
        if not isinstance(way, osm.Way):
            continue

        valid_nodes = [n for n in way.nodes if n.location.valid()]
        
        # Register nodes uniquely
        for n in valid_nodes:
            node_dict[n.ref] = n
        
        # Build edges using node IDs
        for n1, n2 in zip(valid_nodes[:-1], valid_nodes[1:]):
            dist = haversine_np(n1, n2)
            edges_list.append((n1.ref, n2.ref, dist))

    node_id_to_index = {node_id: i for i, node_id in enumerate(node_dict.keys())}

    # Nodes
    nodes_df = pd.DataFrame({
        "x": [n.lon for n in node_dict.values()],
        "y": [n.lat for n in node_dict.values()]
    })

    # Edges
    edges_df = pd.DataFrame(edges_list, columns=["from_id", "to_id", "dist"])
    edges_df["from"] = edges_df["from_id"].map(node_id_to_index)
    edges_df["to"] = edges_df["to_id"].map(node_id_to_index)
    edges_df = edges_df[["from", "to", "dist"]]

    # Pandana edge weights
    edge_weights = pd.DataFrame(edges_df["dist"])

    context.log.info(f"Nodes in network: {len(node_dict)}")
    context.log.info(f"Edges in network: {len(edges_list)}")

    network = pdna.Network(
        nodes_df["x"],
        nodes_df["y"],
        edges_df["from"],
        edges_df["to"],
        edge_weights
    )

    network.save_hdf5(out_path)
    return WalkNetwork(out_path)



