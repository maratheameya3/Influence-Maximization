import igraph as ig

# Create a graph with overlapping and non-overlapping communities
g = ig.Graph()
g.add_vertices(10)
g.add_edges([(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(5,6),(6,7),(7,8),(8,9),(9,5),(5,2),(2,8),(2,7),(5,9)])

# Detect communities using the walktrap algorithm
communities = g.community_walktrap().as_clustering()

for comm in communities:
    print(comm)

# Initialize an empty dictionary to store the boundary nodes
boundary_nodes = {}

# Iterate over the edges and find the boundary nodes
for edge in g.es:
    source = edge.source
    target = edge.target
    source_communities = [c for c in range(len(communities)) if source in communities[c]]
    target_communities = [c for c in range(len(communities)) if target in communities[c]]
    common_communities = set(source_communities).intersection(set(target_communities))
    if len(common_communities) > 1:
        for community_index in common_communities:
            if community_index not in boundary_nodes:
                boundary_nodes[community_index] = set()
            boundary_nodes[community_index].add(source)
            boundary_nodes[community_index].add(target)
    elif len(common_communities) == 1:
        community_index = list(common_communities)[0]
        if community_index not in boundary_nodes:
            boundary_nodes[community_index] = set()
        boundary_nodes[community_index].add(source)
        boundary_nodes[community_index].add(target)

# Print the boundary nodes for each community
for i, nodes in boundary_nodes.items():
    print("Community", i, "boundary nodes:", list(nodes))
