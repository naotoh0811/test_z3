import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import networkx as nx

def gen_edge_labels_from_matrix(g):
    edge_labels = {}
    for hi, costList  in enumerate(g):
        for wi, cost in enumerate(costList):
            if(cost):
                edge_labels[(hi, wi)] = cost

    return edge_labels
    # edge_labels {(0, 1): 10, (0, 3): 20, (1, 2): 30, (3, 4): 40}

def edge_labels_to_edges(edge_labels):
    edges = []
    for edge in edge_labels.keys():
        edges.append(edge)
    return edges
    # edges [(0, 1), (0, 3), (1, 2), (3, 4)]

def gen_graph(edge_labels):
    G = nx.Graph()
    edges = edge_labels_to_edges(edge_labels)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

def gen_pdf(filename):
    pp = PdfPages(filename)
    pp.savefig()
    pp.close()
    plt.clf()

if __name__ == '__main__':
    g = [
        [ 0, 10,  0, 20,  0,  0,  0, 30],
        [10,  0, 10,  0,  0,  0,  0,  0],
        [ 0, 10,  0,  0, 20,  0,  0,  0],
        [20,  0,  0,  0,  0, 20,  0,  0],
        [ 0,  0, 20,  0,  0,  0,  0, 20],
        [ 0,  0,  0, 20,  0,  0, 10,  0],
        [ 0,  0,  0,  0,  0, 10,  0, 10],
        [30,  0,  0,  0, 20,  0, 10,  0]
    ]
    edge_labels = {
        (0, 1): 10,
        (1, 2): 10,
        (4, 7): 20,
        (6, 7): 10,
        (2, 4): 20,
        (5, 6): 10,
        (0, 7): 30,
        (0, 3): 20,
        (3, 5): 20
    }

    #edge_labels = gen_edge_labels_from_matrix(g)
    gen_graph(edge_labels)
    gen_pdf('network.pdf')