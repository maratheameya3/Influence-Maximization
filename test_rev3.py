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

def split_and_calculate(g, loc, k, filename):
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
    print("final influencers", len(final_influencers))
    final_influencers = test_method(final_influencers, threshold, dg, k)
    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    curr_active_nodes = compute_influence_spread(dg, final_influencers, threshold, k)
    print("Final Total number of nodes influenced:", len(curr_active_nodes))
    # print_nodes(curr_active_nodes, g)
    # color_vertex(g, final_influencers, curr_active_nodes)
    # random.seed(123)
    # plot_graph(g, "random", f"{loc}-output-celf-graph-dominating-set.png")

# print("---------------------------------Working for Youtube Dataset---------------------------------")
# g = igraph.read("youtube.edges", format="ncol", directed=True, names = True)
# # K = 12
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# # compute_reach(g, "youtube", K, "youtube.edges")
# split_and_calculate(g, "youtube", 20, "youtube.edges")

print("---------------------------------Working for Facebook Dataset---------------------------------")
g = igraph.read("0.edges", format="ncol", directed=True, names=True)
# K = 50
for vertex in range(0, g.vcount(), 1):
    g.vs[vertex]["label"] = vertex
# compute_reach(g, "facebook", K)
split_and_calculate(g, "0", 40, "0.edges")

# print("---------------------------------Working for Twitter Dataset---------------------------------")
# g = igraph.read("twitter.edges", format="ncol", directed=True, names=True)
# K = 50
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "twitter", K)

# print("---------------------------------Working for GOT Dataset---------------------------------")
# g = igraph.Graph.Read_GraphML('got.graphml')
# K = 50
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["name"] = g.vs[vertex]["label"]
#     g.vs[vertex]["label"] = vertex
# split_and_calculate(g, "GOT", 50, "got.graphml")

# print("---------------------------------Working for Netscience Dataset---------------------------------")
# # g = igraph.read("netscience.edges", format="ncol", directed=False, names=True)
# g = igraph.Graph.Read_GML("netscience.gml")
# # K = 800
# # for vertex in range(0, g.vcount(), 1):
# #     # import pdb; pdb.set_trace()
# #     g.vs[vertex]["label"] = int(g.vs[vertex]["name"])
#     # g.vs[vertex]["name"] = g.vs[vertex].index
# split_and_calculate(g, "netscience", 100, "netscience.gml")

# g = igraph.read("phy.edges", format="ncol", directed=True, names=True)
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# split_and_calculate(g, "crime-moreno", 657, "phy.edges")

# print("---------------------------------Working for Hamsterster Dataset---------------------------------")
# g = igraph.read("soc-hamsterster.edges", format="ncol", directed=True, names = True)
# # K = 100
# for vertex in range(0, g.vcount(), 1):
#     # import pdb; pdb.set_trace()
#     g.vs[vertex]["label"] = g.vs[vertex].index
# # compute_reach(g, "hamsterster", 100)
# split_and_calculate(g, "hamsterster", 600, "soc-hamsterster.edges")

# print("---------------------------------Working for WikiVote Dataset---------------------------------")
# g = igraph.read("soc-wiki-Vote.mtx", format="ncol", directed=True, names = True)
# # K = 100
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "WikiVote", 500)