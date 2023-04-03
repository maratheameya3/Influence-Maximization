import igraph
import random
from collections import OrderedDict
from operator import itemgetter


def get_undirected_graph(g):
   undirected_graph = g.copy()
   undirected_graph.to_undirected()
   return undirected_graph

# def get_dominant_set(graph):
#     graph_undirected = get_undirected_graph(graph)
#     graph_degree_test = graph_undirected.vs.degree()
#     influencers = []
#     graph_degree = [(i, graph_degree_test[i]) for i in range(len(graph_degree_test))]# if graph_degree_test[i] != 0]
#     graph_degree.sort(key=lambda x: x[1], reverse=True)
#     while graph_degree:
#         temp = graph_degree[0]
#         if temp not in influencers:
#             influencers.append(temp[0])
#             neighbors = graph.neighbors(temp[0], mode="ALL")
#             for vertex in neighbors:
#                 graph_degree = [i for i in graph_degree if i[0] != vertex]
#             graph_degree = [i for i in graph_degree if i[0] != temp[0]]
#     return influencers

def get_dominant_set(graph):
    graph_undirected = get_undirected_graph(graph)
    graph_degree_test = graph_undirected.vs.degree()
    dominant_set = set()
    graph_degree = [(i, graph_degree_test[i]) for i in range(len(graph_degree_test)) if i not in dominant_set]# if graph_degree_test[i] != 0]
    graph_degree.sort(key=lambda x: x[1], reverse=True)
    while graph_degree:
        temp = graph_degree[0]
        if temp not in dominant_set:
            dominant_set.add(temp[0])
            neighbors = graph.neighbors(temp[0], mode="ALL")
            for vertex in neighbors:
                graph_degree = [i for i in graph_degree if i[0] != vertex]
            graph_degree = [i for i in graph_degree if i[0] != temp[0]]
    return dominant_set

# def get_dominant_set(graph, K):
#     graph_undirected = get_undirected_graph(graph)
#     betweenness_centrality = graph.betweenness()
#     graph_degree_test = graph_undirected.vs.degree()
#     influencers = []
#     graph_degree = [(i, graph_degree_test[i]) for i in range(len(graph_degree_test))]
#     graph_degree.sort(key=lambda x: x[1], reverse=True)
#     while graph_degree:
#         temp = graph_degree[0]
#         if temp not in influencers:
#             influencers.append(temp[0])
#             neighbors = graph.neighbors(temp[0], mode="ALL")
#             for vertex in neighbors:
#                 graph_degree = [i for i in graph_degree if i[0] != vertex]
#             graph_degree = [i for i in graph_degree if i[0] != temp[0]]
#     betweenness_centrality = [(i, betweenness_centrality[i]) for i in range(len(betweenness_centrality)) if i not in influencers]
#     betweenness_centrality.sort(key=lambda x: x[1], reverse=True)
#     if len(influencers) <= K:
#         trial = betweenness_centrality[:K-len(influencers)]
#         influencers += [i[0] for i in trial]
#     return influencers

# def get_vertex_cover(graph):
#     vertex_cover = set()
#     vertex_degree = dict()
#     graph_undirected = get_undirected_graph(graph)
#     graph_degree = graph_undirected.vs.degree()
#     for num in range(0, len(graph.vs)):
#         vertex_degree[num] = graph_degree[num]
#     vertex_degree_sorted = OrderedDict(sorted(vertex_degree.items(), key=itemgetter(1), reverse= True))
#     vertices =  vertex_degree_sorted.keys()
#     for v in vertices:
#         neighbors = []
#         neighbors = graph.neighbors(v, mode="ALL")
#         neighbors_set = set(neighbors)
#         if v not in vertex_cover:
#             for n in neighbors_set:
#                 if n not in vertex_cover:
#                     vertex_cover.add(v)
#                     break
#     print("!!!!!!!!!!!!!", vertex_cover)
#     return vertex_cover

def get_vertex_cover_actual(graph):
    vertex_cover = set()
    edges = [(i.source, i.target) for i in graph.es]
    while edges:
        curr_choice = random.choice(edges)
        vertex_cover.add(curr_choice[0])
        vertex_cover.add(curr_choice[1])
        for i in graph.vs[curr_choice[0]].neighbors():
            edges = [edge for edge in edges if (edge[0]!=i and edge[1]!=i)]
        for i in graph.vs[curr_choice[1]].neighbors():
            edges = [edge for edge in edges if (edge[0]!=i and edge[1]!=i)]
        edges.remove(curr_choice)
    return vertex_cover