import igraph
from igraph import *
from random import uniform

# Convert undirected to directed graph
def get_directed_graph(g):
    if not g.is_directed():
        g_copy = g.copy()
        g_copy.to_directed(mutual=True)
        edges = set(g_copy.get_edgelist())
        dg = igraph.Graph(directed=True)
        dg.add_vertices(len(g_copy.vs))
        dg.add_edges(edges)
        return dg
    else:
        return g
        
# Assign Weights to edges      
def init_edge_influence(dg):
    degrees = dg.degree(mode="in")
    edge_influence = [0 if degrees[i.target] == 0 else 1/float(degrees[i.target]) for i in dg.es]
    dg.es["influence"] = edge_influence
    return dg
 
    
def init_vertex_threshold(dg):
    vertex_threshold = dict()
    degrees = dg.degree()
    for n in range (0, len(degrees)):
        val = (degrees[n] * 10)/(sum(degrees) * 1.0)
        val = val * 10 if val < 0.1 else val
        val = val if val < 1 else 1
        vertex_threshold[n] = val
    return vertex_threshold

# Calculate the sum of incoming active neighbors   
def sum_edge_influence(dg, active_neighbor, n):
    sum = 0.0
    for src in active_neighbor:
        edge = set(dg.es.select(_source_eq =src, _target_eq =n))
        for e in edge:
            sum = sum + dg.es[dg.get_eid(e.source,e.target)]["influence"]
    return sum if sum < 1.0 else sum

# Compute information diffusionS 
def compute_k_diffusion(dg, k, seed_set, threshold):
    curr_active_nodes = set(seed_set)
    total_influenced = seed_set
    total_k_influenced_nodes = []
    while(True):
        total_k_influenced_nodes = compute_curr_diffusion(dg, curr_active_nodes, threshold)
        if len(total_k_influenced_nodes) == len(total_influenced):
            break
        curr_active_nodes = list( total_k_influenced_nodes)
        total_influenced = list(total_k_influenced_nodes)
    return curr_active_nodes

# Compute diffusion in current round    
def compute_curr_diffusion(dg, seed_set, threshold):
    curr_seed_set = set(seed_set)
    curr_seed_list = list(seed_set)
    for num in range(0, len(curr_seed_list)):
        # import pdb; pdb.set_trace()
        neighbors = dg.successors(int(curr_seed_list[num]))
        for n in neighbors:
            if (n not in curr_seed_list):
                active_neighbor = list(set(dg.predecessors(n)).intersection(set(curr_seed_list)))
                sum = sum_edge_influence(dg, active_neighbor, n)
                if (sum - float(threshold[n])) > 0: 
                     curr_seed_set.add(n)
                curr_seed_list = list(curr_seed_set)
    return curr_seed_list
        
# def compute_curr_diffusion(dg, seed_set, threshold):
#     curr_seed_set = set(seed_set)
#     curr_seed_list = list(seed_set)
    
#     for seed_node in curr_seed_list:
#         neighbors = dg.successors(seed_node)
#         for neighbor in neighbors:
#             if neighbor not in curr_seed_list:
#                 active_neighbors = set(dg.predecessors(neighbor)).intersection(curr_seed_set)
#                 edge_influence_sum = sum_edge_influence(dg, active_neighbors, neighbor)
#                 if edge_influence_sum - float(threshold[neighbor]) > 0: 
#                      curr_seed_set.add(neighbor)
#         curr_seed_list = list(curr_seed_set)
        
#     return curr_seed_list
