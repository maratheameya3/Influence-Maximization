# Based only on the dominant set whatever number that might be

import queue
import random
import time
import igraph
from LinearThreshold import get_directed_graph, init_vertex_threshold, init_edge_influence, compute_k_diffusion
from vertex_cover_rev import get_dominant_set, get_vertex_cover_actual
from joblib import Parallel, delayed
import multiprocessing
from louvain_cd_test import *


class queue_element():
    def __init__(self, idx, i, j):
        self.index = idx
        self.mg = i
        self.iteration = j

    def __lt__(self, other):
        return self.mg < other.mg
     
    def __gt__(self, other):
        return self.mg > other.mg


def test_method(dominant_set, threshold, dg, K):
    influencers = []
    q = queue.PriorityQueue()
    iteration = 1
    if len(dominant_set) < K:
        return dominant_set
    for vertex in dominant_set:
        temp = [vertex]
        curr_mg = compute_spread(dg, temp,threshold, K)
        q.put((-curr_mg, queue_element(vertex, curr_mg, iteration)))
    while True:
        if iteration > K:
            break
        max_element = q.get()[1]
        if max_element.iteration == iteration:
            # print("@@@@@@@@@@@@@@@")
            influencers.append(max_element.index)
            iteration = iteration + 1
        else:
            #  print("$$$$$$$$$$$$$$$$$$$$$$$")
             temp = list( influencers )
             temp.append(max_element.index)
             max_element.iteration = iteration
             curr_mg = compute_spread(dg, temp, threshold, K)
             total_mg = curr_mg - max_element.mg
             q.put((-total_mg,queue_element(max_element.index, total_mg, iteration)))
        # print("#####", iteration)
    return influencers

def compute_influencers_dominating_set(g, dg, threshold, K) :
    influencers = []
    q = queue.PriorityQueue()
    iteration = 1
    dominant_set = get_dominant_set(g)
    start_time = time.time()
    print(len(dominant_set))
    if len(dominant_set) < K:
        return dominant_set
    for vertex in dominant_set:
        temp = [vertex]
        curr_mg = compute_spread(dg, temp,threshold, K)
        q.put((-curr_mg, queue_element(vertex, curr_mg, iteration)))
    print(f"Time required to get influencers using celf dominating set -> {time.time()-start_time}")
    while True:
        if iteration > K:
            break
        max_element = q.get()[1]
        if max_element.iteration == iteration:
            # print("@@@@@@@@@@@@@@@")
            influencers.append(max_element.index)
            iteration = iteration + 1
        else:
            #  print("$$$$$$$$$$$$$$$$$$$$$$$")
             temp = list( influencers )
             temp.append(max_element.index)
             max_element.iteration = iteration
             curr_mg = compute_spread(dg, temp, threshold, K)
             total_mg = curr_mg - max_element.mg
             q.put((-total_mg,queue_element(max_element.index, total_mg, iteration)))
        # print("#####", iteration)
    return influencers

def compute_spread(dg, influencers, threshold, K):
    curr_active_nodes = compute_k_diffusion(dg, K, influencers , threshold)
    active_nodes = set(influencers)
    for c in curr_active_nodes:
        active_nodes.add(c)
    num_active_nodes = len(active_nodes)
    return num_active_nodes
    
def print_nodes(node_list, g):
    record = ""
    print("Influenced Vertices by Id are:")
    print(node_list)
    print("Influenced Vertices by names are:")
    cnt = 0
    for i in node_list:
        if cnt <= 5:
            record =  record + "    " + g.vs[i]["name"] 
            cnt = cnt + 1 
        else:
            record = record + "\n"
            cnt = 0
    print(record)

def compute_influence_spread(dg, seed_set, threshold, K):
    print("$$$$$$$$$$$", len(seed_set))
    curr_active_nodes = set()
    influencers_set = set()
    for n in seed_set:
        influencers_set.add(n)
        curr_active_nodes.add(n)
    curr_active_nodes = compute_k_diffusion(dg, K,  influencers_set , threshold)
    return curr_active_nodes

def color_vertex(g,influencer_list, spread_list):
    for i in range(0,g.vcount(),1):
        g.vs[i]["color"] = "red" if g.vs[i]["label"] in influencer_list else \
            "green" if g.vs[i]["label"] in spread_list else "blue"
    return g

def plot_graph(graph, layoutType, filename):
    igraph.plot(graph,
                filename,
                vertex_size=30,
                layout=layoutType,
                bbox=(1000,1000),
                margin=30)

def get_overlapping_boundary_nodes(g, partitions):
    obns = []
    for partition in partitions:
        subgraph = g.subgraph(partition)
        all_vertices = set(subgraph.vs)
        interior_vertices = set(subgraph.vs.select(_neighborhood=all_vertices))
        boundary_vertices = all_vertices - interior_vertices
        obns.extend(list(boundary_vertices))
    obns = [i]
    return obns

def get_community_boundary_nodes(partitions):
    cbns = set()
    for i, community in enumerate(partitions):
        for j, other_community in enumerate(partitions):
            if i != j:
                cbns.update(set(community) & set(other_community))
    return cbns

def split_and_calculate(g, loc, k, filename):
    g.vs["color"] = "blue"
    read_ip(filename)
    init_variables()
    partitions, _ = start_louvain()
    final_influencers = []
    partitionslen = [len(partition) for partition in partitions]
    print(partitionslen)
    for partition in partitions:
        subgraph = g.subgraph(partition)
        final_influencers.extend(get_dominant_set(subgraph))
    
    dg = get_directed_graph(g)
    dg = init_edge_influence(dg)
    threshold = init_vertex_threshold(dg)
    final_influencers = list(set(final_influencers))
    cbns = get_community_boundary_nodes(partitions)
    obns = get_overlapping_boundary_nodes(g, partitions)
    for i in cbns:
        if i not in final_influencers:
            final_influencers.add(i)
    for i in obns:
        if i not in final_influencers:
            final_influencers.append(i)
    final_influencers = list(set(final_influencers))
    print("final influencers", len(final_influencers))
    final_influencers = test_method(final_influencers, threshold, dg, k)
    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    curr_active_nodes = compute_influence_spread(dg, final_influencers, threshold, k)
    print("Final Total number of nodes influenced:", len(curr_active_nodes))
    print_nodes(curr_active_nodes, g)
    color_vertex(g, final_influencers, curr_active_nodes)
    random.seed(123)
    plot_graph(g, "random", f"{loc}-output-celf-graph-dominating-set.png")

print("---------------------------------Working for Facebook Dataset---------------------------------")
g = igraph.read("../data/0.edges", format="ncol", directed=True, names=True)
for vertex in range(0, g.vcount(), 1):
    g.vs[vertex]["label"] = vertex
split_and_calculate(g, "0", 30, "../data/0.edges")
