from igraph import Graph
from queue import PriorityQueue

graph = Graph.Read("phy.edges", format="ncol")
directed_graph = graph.to_directed()
dg = Graph(directed=True)
dg = Graph(directed=True)
dg.add_vertices(len(graph.vs))
dg.add_edges(graph.get_edgelist())

edges = []

for i in graph.es:
    edges.append(((i.source, i.target), 1))

degrees = dg.degree()
in_degrees = dg.degree(mode="in")
out_degrees = dg.degree(mode="out")
sum_degrees = sum(degrees)
edge_influence = []

for i in range(len(in_degrees)):
    edge_influence.append(1/in_degrees[edges[i][0][1]])

thresholds = []

for i in range(len(graph.vs)):
    degree_val = in_degrees[i] + out_degrees[i]
    threshold = ((degrees[i] * 10) / sum_degrees * 1.0)
    thresholds.append((threshold * 10) if threshold < 0.1 else 1.0)

marginal_gains = PriorityQueue()
for i in graph.vs:
    neighbors = graph.vs[i.index].neighbors()
    import pdb; pdb.set_trace()
    print("jdkfjsdlf")

# def compute_diffusion():
#     return

import pdb; pdb.set_trace()

print("Hello")