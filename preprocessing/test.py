# https://docs.osmcode.org/pyosmium/latest/user_manual/04-Working-with-Filters/
import osmium
from osmium import filter, osm
import math
import pandas as pd
import pandana as pdna

data= "../../denmark-260208.osm.pbf"
fp = osmium.FileProcessor(data).with_locations() \
    .with_filter(filter.EntityFilter(osm.WAY)) \
    .with_filter(filter.KeyFilter("highway")
)

def pythagoras(node1, node2):
    a = node1.lon - node2.lon
    b = node1.lat - node2.lat
    return math.hypot(a, b)

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
        dist = pythagoras(n1, n2)
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

print(len(node_dict))
print(len(edges_list))

network = pdna.Network(
    nodes_df["x"],
    nodes_df["y"],
    edges_df["from"],
    edges_df["to"],
    edge_weights
)

#network.save_hdf5("denmark.backup")