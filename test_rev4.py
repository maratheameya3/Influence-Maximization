import queue
import random
import time
import igraph
from LinearThreshold import get_directed_graph, init_vertex_threshold, init_edge_influence, compute_k_diffusion
from vertex_cover import get_dominant_set, get_vertex_cover_actual
from joblib import Parallel, delayed
import multiprocessing
from louvain_cd_new import *


class queue_element():
    def __init__(self, idx, i, j):
        self.index = idx
        self.mg = i
        self.iteration = j

    def __lt__(self, other):
        return self.mg < other.mg
     
    def __gt__(self, other):
        return self.mg > other.mg


def compute_influence_spread(dg, seed_set, threshold, K):
    curr_active_nodes = set()
    influencers_set = set()
    for n in seed_set:
        influencers_set.add(n)
        curr_active_nodes.add(n)
    curr_active_nodes = compute_k_diffusion(dg, K,  influencers_set , threshold)
    return curr_active_nodes


def calc_coverage(community_degrees, cur_influencers):
    if community_degrees == 0:
        coverage = 100
    else:
        coverage = sum(g.degree([i[0] for i in cur_influencers])) / community_degrees * 100
    return coverage


def compute_reach_pagerank(g, k, filename):
    read_ip(filename)
    init_variables()
    partitions, _ = start_louvain()
    influencers = []

    for partition in partitions:
        subgraph = g.subgraph(partition)
        pagerank_values = subgraph.pagerank()
        pageranks = []
        for i, j in zip(subgraph.vs, pagerank_values):
            pageranks.append((i['label'], j))
        pageranks.sort(key=lambda x: x[1], reverse=True)
        num_influencers = (20/100*len(partition)).__ceil__()
        cur_influencers = pageranks[:num_influencers]
        community_degrees = sum(g.degree(partition))
        coverage = calc_coverage(community_degrees, cur_influencers)
        temp = 50
        while coverage < 70:
            num_influencers = ((temp + 5)/100*len(partition)).__ceil__()
            cur_influencers = pageranks[:num_influencers]
            temp += 10
            coverage = calc_coverage(community_degrees, cur_influencers)
        print(cur_influencers)
        influencers.extend(cur_influencers)
        coverage = calc_coverage(community_degrees, cur_influencers)

    print("Number of nodes -> ", len(g.vs))
    print("Number of edges -> ", len(g.es))

    dg = get_directed_graph(g)
    dg = init_edge_influence(dg)
    threshold = init_vertex_threshold(dg)

    temp = [inf[0] for inf in influencers]
    pagerank_values = g.pagerank()
    influencers.sort(key=lambda x: x[1], reverse=True)
    for i, j in zip(g.vs, pagerank_values):
            if i['label'] in temp:
                pageranks.append((i['label'], j))
    influencers = pageranks[:k]

    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    print("!!!!!!!!!!!!!!!", len(influencers))
    curr_active_nodes = compute_influence_spread(dg, [inf[0] for inf in influencers], threshold, k)
    print("Total number of nodes influenced:", len(curr_active_nodes))


def compute_reach_betweenness(g, k, filename):
    read_ip(filename)
    init_variables()
    partitions, _ = start_louvain()
    influencers = []

    for partition in partitions:
        subgraph = g.subgraph(partition)
        betweenness_values = subgraph.betweenness()
        betweennesss = []
        for i, j in zip(subgraph.vs, betweenness_values):
            betweennesss.append((i['label'], j))
        betweennesss.sort(key=lambda x: x[1], reverse=True)
        num_influencers = (20/100*len(partition)).__ceil__()
        cur_influencers = betweennesss[:num_influencers]
        community_degrees = sum(g.degree(partition))
        coverage = calc_coverage(community_degrees, cur_influencers)
        temp = 50
        while coverage < 70:
            num_influencers = ((temp + 5)/100*len(partition)).__ceil__()
            cur_influencers = betweennesss[:num_influencers]
            temp += 10
            coverage = calc_coverage(community_degrees, cur_influencers)
        print(cur_influencers)
        influencers.extend(cur_influencers)
        coverage = calc_coverage(community_degrees, cur_influencers)

    print("Number of nodes -> ", len(g.vs))
    print("Number of edges -> ", len(g.es))

    dg = get_directed_graph(g)
    dg = init_edge_influence(dg)
    threshold = init_vertex_threshold(dg)

    temp = [inf[0] for inf in influencers]
    betweenness_values = g.betweenness()
    influencers.sort(key=lambda x: x[1], reverse=True)
    for i, j in zip(g.vs, betweenness_values):
            if i['label'] in temp:
                betweennesss.append((i['label'], j))
    influencers = betweennesss[:k]

    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    print("!!!!!!!!!!!!!!!", len(influencers))
    curr_active_nodes = compute_influence_spread(dg, [inf[0] for inf in influencers], threshold, k)
    print("Total number of nodes influenced:", len(curr_active_nodes))

def compute_reach_eigen_vector(g, k, filename):
    read_ip(filename)
    init_variables()
    partitions, _ = start_louvain()
    influencers = []

    for partition in partitions:
        subgraph = g.subgraph(partition)
        eigen_vector_values = subgraph.eigenvector_centrality()
        eigen_vectors = []
        for i, j in zip(subgraph.vs, eigen_vector_values):
            eigen_vectors.append((i['label'], j))
        eigen_vectors.sort(key=lambda x: x[1], reverse=True)
        num_influencers = (20/100*len(partition)).__ceil__()
        cur_influencers = eigen_vectors[:num_influencers]
        community_degrees = sum(g.degree(partition))
        coverage = calc_coverage(community_degrees, cur_influencers)
        temp = 50
        while coverage < 70:
            num_influencers = ((temp + 5)/100*len(partition)).__ceil__()
            cur_influencers = eigen_vectors[:num_influencers]
            temp += 10
            coverage = calc_coverage(community_degrees, cur_influencers)
        print(cur_influencers)
        influencers.extend(cur_influencers)
        coverage = calc_coverage(community_degrees, cur_influencers)

    print("Number of nodes -> ", len(g.vs))
    print("Number of edges -> ", len(g.es))

    dg = get_directed_graph(g)
    dg = init_edge_influence(dg)
    threshold = init_vertex_threshold(dg)

    temp = [inf[0] for inf in influencers]
    eigen_vector_values = g.eigenvector_centrality()
    influencers.sort(key=lambda x: x[1], reverse=True)
    for i, j in zip(g.vs, eigen_vector_values):
            if i['label'] in temp:
                eigen_vectors.append((i['label'], j))
    influencers = eigen_vectors[:k]

    print("Computing the spread of seed set ....")
    curr_active_nodes = set()
    print("!!!!!!!!!!!!!!!", len(influencers))
    curr_active_nodes = compute_influence_spread(dg, [inf[0] for inf in influencers], threshold, k)
    print("Total number of nodes influenced:", len(curr_active_nodes))


# print("---------------------------------Working for Karate Dataset---------------------------------")
# g = igraph.Graph.Read_GraphML('karate.GraphML')
# # K = 3
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "karate", 12)

# print("---------------------------------Working for Twitter Dataset---------------------------------")
# g = igraph.read("twitter.edges", format="ncol", directed=True, names=True)
# # K = 50
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, 110, "twitter.edges")

# print("---------------------------------Working for GOT Dataset---------------------------------")
# g = igraph.Graph.Read_GraphML('got.graphml')
# K = 50
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["name"] = g.vs[vertex]["label"]
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "GOT", K)

print("---------------------------------Working for Netscience Dataset---------------------------------")
g = igraph.Graph.Read_GML('netscience.gml')
# g = igraph.read("netscience.edges", format="ncol", directed=True, names=True)
# K = 800
for vertex in range(0, g.vcount(), 1):
    g.vs[vertex]["label"] = int(g.vs[vertex]["id"])
compute_reach_eigen_vector(g, 160, "netscience.gml")

# print("---------------------------------Working for Facebook Dataset---------------------------------")
# g = igraph.read("0.edges", format="ncol", directed=True, names=True)
# K = 50
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "facebook", K)

# g = igraph.read("phy.edges", format="ncol", directed=True, names=True)
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, "crime-moreno")

# print("---------------------------------Working for Hamsterster Dataset---------------------------------")
# g = igraph.read("soc-hamsterster.edges", format="ncol", directed=True, names = True)
# # K = 500
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach(g, 600, "soc-hamsterster.edges")

# print("---------------------------------Working for WikiVote Dataset---------------------------------")
# g = igraph.read("soc-wiki-Vote.mtx", format="ncol", directed=True, names = True)
# # K = 100
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# compute_reach_betweenness(g, 300, "soc-wiki-Vote.mtx")