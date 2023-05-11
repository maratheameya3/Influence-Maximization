import igraph
from LinearThreshold import get_directed_graph, init_vertex_threshold, init_edge_influence, compute_k_diffusion
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

def get_partitions(filename):
    read_ip(filename)
    init_variables()
    partitions, _ = start_louvain()
    return partitions

def compute_reach_pagerank(g, k, partitions):
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

    print("Computing the spread of seed set with pagerank centralities in communities....")
    curr_active_nodes = set()
    print("!!!!!!!!!!!!!!!", len(influencers))
    curr_active_nodes = compute_influence_spread(dg, [inf[0] for inf in influencers], threshold, k)
    print("Total number of nodes influenced:", len(curr_active_nodes))
    return len(curr_active_nodes)

def compute_reach_betweenness(g, k, partitions):
    influencers = []
    for partition in partitions:
        subgraph = g.subgraph(partition)
        betweenness_values = subgraph.betweenness()
        betweenness = []
        for i, j in zip(subgraph.vs, betweenness_values):
            betweenness.append((i['label'], j))
        betweenness.sort(key=lambda x: x[1], reverse=True)
        num_influencers = (20/100*len(partition)).__ceil__()
        cur_influencers = betweenness[:num_influencers]
        community_degrees = sum(g.degree(partition))
        coverage = calc_coverage(community_degrees, cur_influencers)
        temp = 50
        while coverage < 70:
            num_influencers = ((temp + 5)/100*len(partition)).__ceil__()
            cur_influencers = betweenness[:num_influencers]
            temp += 10
            coverage = calc_coverage(community_degrees, cur_influencers)
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
                betweenness.append((i['label'], j))
    influencers = betweenness[:k]

    print("Computing the spread of seed set using the betweenness centralities....")
    curr_active_nodes = set()
    print("!!!!!!!!!!!!!!!", len(influencers))
    curr_active_nodes = compute_influence_spread(dg, [inf[0] for inf in influencers], threshold, k)
    print("Total number of nodes influenced:", len(curr_active_nodes))
    return len(curr_active_nodes)

def compute_reach_eigen_vector(g, k, partitions):
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

    print("Computing the spread of seed set using the eigenvector centralities....")
    curr_active_nodes = set()
    print("!!!!!!!!!!!!!!!", len(influencers))
    curr_active_nodes = compute_influence_spread(dg, [inf[0] for inf in influencers], threshold, k)
    print("Total number of nodes influenced:", len(curr_active_nodes))
    return len(curr_active_nodes)

print("---------------------------------Working for twitter Dataset---------------------------------")
g = igraph.read('../data/twitter.edges', format="ncol", directed=True, names=True)
K = 10
for vertex in range(0, g.vcount(), 1):
    g.vs[vertex]["label"] = int(g.vs[vertex].index)
partitions = get_partitions("../data/twitter.edges")
tot_pagerank = 0
tot_betweenness = 0
tot_eigenvector = 0
for i in range(5):
    tot_pagerank += compute_reach_pagerank(g, K, partitions)
print("Average is ", tot_pagerank//5)
for i in range(5):
    tot_betweenness += compute_reach_betweenness(g, K, partitions)
print("Average is ", tot_betweenness//5)
for i in range(5):
    tot_eigenvector += compute_reach_eigen_vector(g, K, partitions)
print("Average is ", tot_eigenvector//5)

# print("---------------------------------Working for Netscience Dataset---------------------------------")
# g = igraph.Graph.Read_GML('../data/netscience.gml')
# K = 800
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = int(g.vs[vertex]["id"])
# partitions = get_partitions("../data/netscience.gml")
# compute_reach_pagerank(g, K, partitions)
# compute_reach_betweenness(g, K, partitions)
# compute_reach_eigen_vector(g, K, partitions)

# print("---------------------------------Working for Hamsterster Dataset---------------------------------")
# g = igraph.read("../data/soc-hamsterster.edges", format="ncol", directed=True, names = True)
# K = 1600
# for vertex in range(0, g.vcount(), 1):
#     g.vs[vertex]["label"] = vertex
# partitions = get_partitions("../data/soc-hamsterster.edges")
# compute_reach_pagerank(g, K, partitions)
# compute_reach_betweenness(g, K, partitions)
# compute_reach_eigen_vector(g, K, partitions)