import queue
import random
import time
import igraph
from vertex_cover import get_dominant_set, get_vertex_cover_actual
from LinearThreshold import get_directed_graph, init_vertex_threshold, init_edge_influence, compute_k_diffusion


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
    curr_active_nodes = set()
    influencers_set = set()
    for n in seed_set:
        influencers_set.add(n)
        curr_active_nodes.add(n)
    curr_active_nodes = compute_k_diffusion(dg, K,  influencers_set , threshold)
    return curr_active_nodes

def color_vertex(g,influencer_list, spread_list):
    for i in range(0,g.vcount(),1):
        g.vs[i]["color"] = "yellow" if g.vs[i]["label"] in influencer_list else \
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

    plot_graph(g, "random", "graph.png")

    dg = get_directed_graph(g)
    dg = init_edge_influence(dg)
    threshold = init_vertex_threshold(dg)

    print("Computing influencers by CELF using Dominant Set ....")
    influencers_celf = []
    influencers_celf = compute_influencers_dominating_set(g, dg, threshold, K)
    # print_nodes(influencers_celf, g)

    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    curr_active_nodes = compute_influence_spread(dg, influencers_celf, threshold, K)
    print("Total number of nodes influenced:", len(curr_active_nodes))
    # print_nodes(curr_active_nodes, g)
    color_vertex(g, influencers_celf, curr_active_nodes)
    random.seed(123)
    plot_graph(g, "random", f"{dataset}-output-celf-graph-dominating-set.png")

    print("Computing influencers by CELF using Vertex Cover ....")
    influencers_celf = []
    influencers_celf = compute_influencers_vertex_cover(g, dg, threshold, K)
    # print_nodes(influencers_celf, g)

    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    curr_active_nodes = compute_influence_spread(dg, influencers_celf, threshold, K)
    print("Total number of nodes influenced:", len(curr_active_nodes))
    # print_nodes(curr_active_nodes, g)
    color_vertex(g, influencers_celf, curr_active_nodes)
    random.seed(123)
    plot_graph(g, "random", f"{dataset}-output-celf-graph-vertex-cover.png")



# print("---------------------------------Working for Karate Dataset---------------------------------")
# g = igraph.Graph.Read_GraphML('../data/karate.GraphML')
# K = 2
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "karate", K)

# print("---------------------------------Working for Youtube Dataset---------------------------------")
# g = igraph.read("../data/youtube.edges", format="ncol", directed=True, names = True)
# K = 15
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "youtube", K)

print("---------------------------------Working for Facebook Dataset---------------------------------")
g = igraph.read("../data/0.edges", format="ncol", directed=True, names=True)
K = 50
for vertex in range(0, g.vcount(), 1):
    g.vs[vertex]["label"] = vertex
compute_reach(g, "facebook", K)

# print("---------------------------------Working for GOT Dataset---------------------------------")
# g = igraph.Graph.Read_GraphML('../data/got.graphml')
# K = 40
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["name"] = g.vs[vertex]["label"]
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "GOT", K)

# print("---------------------------------Working for Twitter Dataset---------------------------------")
# g = igraph.read("../data/twitter.edges", format="ncol", directed=True, names = True)
# K = 110
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "twitter", K)

# print("---------------------------------Working for Netscience Dataset---------------------------------")
# g = igraph.Graph.Read_GML('../data/netscience.gml')
# K = 640
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["name"] = g.vs[vertex]["label"]
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "netscience", K)
