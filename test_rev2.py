import queue
import random
import time
import igraph
from LinearThreshold import get_directed_graph, init_vertex_threshold, init_edge_influence, compute_k_diffusion
from vertex_cover import get_dominant_set, get_vertex_cover_actual
from joblib import Parallel, delayed
import multiprocessing
from louvain_cd import *


class queue_element():
    def __init__(self, idx, i, j):
        self.index = idx
        self.mg = i
        self.iteration = j

    def __lt__(self, other):
        return self.mg < other.mg
     
    def __gt__(self, other):
        return self.mg > other.mg


def compute_influencers_vertex_cover(g, dg, threshold, K) :
    influencers = []
    q = queue.PriorityQueue()
    iteration = 1
    vertex_cover = get_vertex_cover_actual(dg)
    start_time = time.time()
    print(len(vertex_cover))
    for vertex in vertex_cover:
        temp = [vertex]
        curr_mg = compute_spread(dg, temp,threshold, K)
        q.put((-curr_mg, queue_element(vertex, curr_mg, iteration)))
    print(f"Time required to get influencers using celf vertex cover -> {time.time()-start_time}")
    while True:
        if iteration > K:
            break
        max_element = q.get()[1]
        if max_element.iteration == iteration:
            influencers.append(max_element.index)
            iteration = iteration + 1
        else:
            temp = list( influencers )
            temp.append(max_element.index)
            max_element.iteration = iteration
            curr_mg = compute_spread(dg, temp, threshold, K)
            total_mg = curr_mg - max_element.mg
            q.put((-total_mg,queue_element(max_element.index, total_mg, iteration)))
        
    return influencers

def compute_influencers_dominating_set(g, dg, threshold, K) :
    influencers = []
    q = queue.PriorityQueue()
    iteration = 1
    dominant_set = get_dominant_set(g, K)
    start_time = time.time()
    print(len(dominant_set))
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
            influencers.append(max_element.index)
            iteration = iteration + 1
        else:
             temp = list( influencers )
             temp.append(max_element.index)
             max_element.iteration = iteration
             curr_mg = compute_spread(dg, temp, threshold, K)
             total_mg = curr_mg - max_element.mg
             q.put((-total_mg,queue_element(max_element.index, total_mg, iteration)))
        
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
    print("$$$$$$$", len(seed_set))
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

def compute_reach(g, dataset, K):
    g.vs["color"] = "blue"

    print("Number of nodes -> ", len(g.vs))
    print("Number of edges -> ", len(g.es))

    # plot_graph(g, "kk", "graph.png")

    dg = get_directed_graph(g)
    dg = init_edge_influence(dg)
    threshold = init_vertex_threshold(dg)

    print("Computing influencers by CELF using Dominant Set ....")
    influencers_dominating = []
    influencers_dominating = compute_influencers_dominating_set(g, dg, threshold, K)
    # print_nodes(influencers_dominating, g)

    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    curr_active_nodes = compute_influence_spread(dg, influencers_dominating, threshold, K)
    print("Total number of nodes influenced:", len(curr_active_nodes))
    # print_nodes(curr_active_nodes, g)
    # color_vertex(g, influencers_dominating, curr_active_nodes)
    # random.seed(123)
    # plot_graph(g, "random", f"{dataset}-output-celf-graph-dominating-set.png")

    # print("Computing influencers by CELF using Vertex Cover ....")
    # influencers_vertex_cover = []
    # influencers_vertex_cover = compute_influencers_vertex_cover(g, dg, threshold, K)
    # # print_nodes(influencers_vertex_cover, g)

    # print("Computing the spread of seed set ....")
    # curr_active_nodes = set()
    # curr_active_nodes = compute_influence_spread(dg, influencers_vertex_cover, threshold, K)
    # print("Total number of nodes influenced:", len(curr_active_nodes))
    # # print_nodes(curr_active_nodes, g)
    # color_vertex(g, influencers_vertex_cover, curr_active_nodes)
    # random.seed(123)
    # plot_graph(g, "random", f"{dataset}-output-celf-graph-vertex-cover.png")
    
    return influencers_dominating, curr_active_nodes


def check_k_value(g, dataset, k):
    first_iter, first_inf = compute_reach(g, dataset, k)
    if k * 2 >= len(g.vs):
        return first_iter
    second_iter, second_inf  = compute_reach(g, dataset, k*2)
    if k * 3 >= len(g.vs):
        if len(second_inf) > len(first_inf):
            return second_iter
        return first_iter
    third_iter, third_inf = compute_reach(g, dataset, k*3)
    if len(third_inf) > len(second_inf):
        return third_iter
    return second_iter

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

def split_and_calculate(g, loc, k, filename):
    read_ip(filename)
    init_variables()
    partitions, _ = start_louvain()
    final_influencers = []
    partitionslen = [len(partition) for partition in partitions]
    print(partitionslen)
    for partition in partitions:
        subgraph = g.subgraph(partition)
        if k >= len(subgraph.vs):
            final_influencers.extend([int(i["id"]) for i in subgraph.vs])
            continue
        cur_inf = check_k_value(subgraph, loc, k)
        final_influencers.extend(cur_inf)
        final_influencers = list(set(final_influencers))
    print("final influencers", len(final_influencers))
    print("!!!!!!!!!!!!", final_influencers)
    
    dg = get_directed_graph(g)
    dg = init_edge_influence(dg)
    threshold = init_vertex_threshold(dg)
    final_influencers = test_method(final_influencers, threshold, dg, k)
    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    curr_active_nodes = compute_influence_spread(dg, final_influencers, threshold, k)
    print("Final Total number of nodes influenced:", len(curr_active_nodes))
    # print_nodes(curr_active_nodes, g)
    # color_vertex(g, final_influencers, curr_active_nodes)
    # random.seed(123)
    # plot_graph(g, "random", f"{loc}-output-celf-graph-dominating-set.png")

print("---------------------------------Working for Youtube Dataset---------------------------------")
g = igraph.read("youtube.edges", format="ncol", directed=True, names = True)
# K = 12
for vertex in range(0, g.vcount(), 1):
    g.vs[vertex]["label"] = vertex
# compute_reach(g, "youtube", K, "youtube.edges")
split_and_calculate(g, "youtube", 15, "youtube.edges")

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
# compute_reach(g, "GOT", K)

# print("---------------------------------Working for Netscience Dataset---------------------------------")
# # g = igraph.read("netscience.edges", format="ncol", directed=False, names=True)
# g = igraph.Graph.Read_GML("netscience.gml")
# # K = 800
# # for vertex in range(0, g.vcount(), 1):
# #     # import pdb; pdb.set_trace()
# #     g.vs[vertex]["label"] = int(g.vs[vertex]["name"])
#     # g.vs[vertex]["name"] = g.vs[vertex].index
# split_and_calculate(g, "netscience", 800, "netscience.gml")

# print("---------------------------------Working for Facebook Dataset---------------------------------")
# g = igraph.read("0.edges", format="ncol", directed=True, names=True)
# K = 50
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# # compute_reach(g, "facebook", K)
# split_and_calculate(g, "0", 5, "0.edges")

# g = igraph.read("phy.edges", format="ncol", directed=True, names=True)
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "crime-moreno")

# print("---------------------------------Working for Hamsterster Dataset---------------------------------")
# g = igraph.read("soc-hamsterster.edges", format="ncol", directed=True, names = True)
# K = 100
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "hamsterster", K)

# print("---------------------------------Working for WikiVote Dataset---------------------------------")
# g = igraph.read("soc-wiki-Vote.mtx", format="ncol", directed=True, names = True)
# K = 100
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "WikiVote", K)