import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import networkx as nx
import pandas as pd

def gen_edge_labels_from_matrix(networkMatrix):
    edge_labels = {}
    for hi, costList  in enumerate(networkMatrix):
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

def gen_graph(edge_labels, color_list):
    G = nx.Graph()
    edges = edge_labels_to_edges(edge_labels)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos)
    nx.draw_networkx_nodes(G, pos, node_color=color_list)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

def gen_pdf(filename):
    pp = PdfPages(filename)
    pp.savefig()
    pp.close()
    plt.clf()

def csv_to_edge_labels(filename):
    df = pd.read_csv(filename)
    edge_labels = {}
    for row in df.itertuples():
        nodeFrom = row.nodeFrom
        nodeTo = row.nodeTo
        cost = row.cost
        edge_labels[(nodeFrom, nodeTo)] = cost
    
    return edge_labels

def csv_to_sw_list(filename):
    df = pd.read_csv(filename)
    sw_list = []
    cli_list = []
    for row in df.itertuples():
        sw_list = row.sw.split()
        sw_list = [int(i) for i in sw_list]
        cli_list = row.cli.split()
        cli_list = [int(i) for i in cli_list]
    
    return sw_list, cli_list

def sw_list_to_color_list(sw_list, cli_list):
    node_num = len(sw_list) + len(cli_list)
    color_list = []
    for node in range(node_num):
        if node in sw_list:
            color_list.append("salmon")
        else:
            color_list.append("lightblue")
    
    return color_list

if __name__ == '__main__':
    networkMatrix = [
        [ 0, 10,  0, 20,  0,  0,  0, 30],
        [10,  0, 10,  0,  0,  0,  0,  0],
        [ 0, 10,  0,  0, 20,  0,  0,  0],
        [20,  0,  0,  0,  0, 20,  0,  0],
        [ 0,  0, 20,  0,  0,  0,  0, 20],
        [ 0,  0,  0, 20,  0,  0, 10,  0],
        [ 0,  0,  0,  0,  0, 10,  0, 10],
        [30,  0,  0,  0, 20,  0, 10,  0]
    ] # not used

    #edge_labels = gen_edge_labels_from_matrix(networkMatrix)

    edge_labels = csv_to_edge_labels('network.csv')
    sw_list, cli_list = csv_to_sw_list('node.csv')
    color_list = sw_list_to_color_list(sw_list, cli_list)
    gen_graph(edge_labels, color_list)
    gen_pdf('network.pdf')