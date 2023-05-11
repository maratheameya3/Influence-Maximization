import os
import igraph
import numpy as np
import matplotlib.pyplot as plt
from igraph import GraphBase, Graph

def save_graph_hist(file_name, output_file_name):
    loc = f"../data/{file_name}"
    ext = os.path.splitext(loc)[-1].lower()
    if ext == ".edges" or ext == ".mtx":
        graph = igraph.read(loc, format="ncol", directed=True)
    if ext == ".gml":
        graph = igraph.Graph.Read_GML(loc)
    if ext == ".graphml":
        graph = igraph.Graph.Read_GraphML(loc)
    degree = graph.degree()

    degree_hist, degree_bin_edges = np.histogram(degree, bins=np.arange(np.max(degree) + 2))
    plt.bar(degree_bin_edges[:-1], degree_hist, width=1)
    plt.xlabel("Degree")
    plt.ylabel("Number of nodes")
    plt.savefig(f"{output_file_name}_histogram.png")

def save_graph_density(file_name, output_file_name):
    loc = f"../data/{file_name}"
    ext = os.path.splitext(loc)[-1].lower()
    if ext == ".edges" or ext == ".mtx":
        graph = igraph.read(loc, format="ncol", directed=True)
    if ext == ".gml":
        graph = igraph.Graph.Read_GML(loc)
    if ext == ".graphml":
        graph = igraph.Graph.Read_GraphML(loc)
    density = graph.density()
    layout = graph.layout_circle()

    igraph.plot(graph, layout=layout)

    igraph.plot([], bbox=(0, 0, 300, 100), main="Density = %.3f" % density)

    cairo_plot = igraph.plot(graph, layout=layout)
    cairo_plot.save(f"{output_file_name}_density_circular.png")

    plt.hist(density, bins=20)
    plt.xlabel('Edge Density')
    plt.ylabel('Frequency')
    plt.title('Histogram of Edge Densities')

    plt.savefig(f'{output_file_name}_density_hist.png')
    print("The degree of the graph is ", density)

def save_graph_powerlaw(file_name, output_file_name):
    loc = f"../data/{file_name}"
    ext = os.path.splitext(loc)[-1].lower()
    if ext == ".edges" or ext == ".mtx":
        graph = igraph.read(loc, format="ncol", directed=True)
    if ext == ".gml":
        graph = igraph.Graph.Read_GML(loc)
    if ext == ".graphml":
        graph = igraph.Graph.Read_GraphML(loc)
    gamma = 2.5
    n = len(graph.vs)
    degree_seq = np.random.pareto(gamma, n)
    degree_sum = int(sum(degree_seq))

    if degree_sum % 2 != 0:
        idx = np.random.randint(n)
        degree_seq[idx] += 1
    igraph.plot(g, bbox=(300, 300))
    fit = igraph.power_law_fit(degree_seq)
    igraph.plot(fit)
    igraph.plot(fit, target=f'{output_file_name}_powerlaw.png')


# save_graph_hist("0.edges", "fb")
# save_graph_hist("youtube.edges", "yt")
# save_graph_hist("twitter.edges", "tw")
# save_graph_hist("netscience.gml", "ns")
# save_graph_hist("soc-hamsterster.edges", "hs")

# print("Facebook")
# save_graph_density("0.edges", "fb")
# print("Youtube")
# save_graph_density("youtube.edges", "yt")
# print("Twitter")
# save_graph_density("twitter.edges", "tw")
# print("Netscience")
# save_graph_density("netscience.gml", "ns")
# print("Hamsterster")
# save_graph_density("soc-hamsterster.edges", "hs")

save_graph_powerlaw("0.edges", "fb")
save_graph_powerlaw("youtube.edges", "yt")
save_graph_powerlaw("twitter.edges", "tw")
save_graph_powerlaw("netscience.gml", "ns")
save_graph_powerlaw("soc-hamsterster.edges", "hs")
