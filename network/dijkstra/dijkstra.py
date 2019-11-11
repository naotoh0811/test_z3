import pandas as pd
import os.path

INFTY = 10000000
WHITE = 0 # unfixed
BLACK = 1 # fixed

def get_path_using_dijkstra(matrix, i_srcNode, i_dstNode):
    size = len(matrix)

    # init
    cost_list = [INFTY] * size
    color_list = [WHITE] * size
    prevNode_list = [-1] * size

    # srcNode
    cost_list[i_srcNode] = 0
    prevNode_list[i_srcNode] = i_srcNode

    while True:
        minCost = INFTY
        i_minNode = -1

        # search node which has minimum cost
        for i in range(size):
            if minCost > cost_list[i] and color_list[i] != BLACK:
                i_minNode = i
                minCost = cost_list[i]
        if i_minNode == -1:
            break
        color_list[i_minNode] = BLACK

        for i_adjNode in range(size):
            if color_list[i_adjNode] != BLACK and matrix[i_minNode][i_adjNode] != INFTY:
                # update cost and prevNode
                if cost_list[i_adjNode] > cost_list[i_minNode] + matrix[i_minNode][i_adjNode]:
                    cost_list[i_adjNode] = cost_list[i_minNode] + matrix[i_minNode][i_adjNode]
                    prevNode_list[i_adjNode] = i_minNode

    # result
    i_prevprevNode = prevNode_list[i_dstNode]
    path = []
    while i_prevprevNode != i_srcNode:
        path.append(i_prevprevNode)
        i_prevprevNode = prevNode_list[i_prevprevNode]
    path = list(reversed(path))
    path.insert(0, i_srcNode)
    path.append(i_dstNode)

    return path

def get_size_from_node_csv(csv_filename):
    df = pd.read_csv(csv_filename)
    for row in df.itertuples():
        cli_list = row.cli.split()
        sw_list = row.sw.split()
    
    return len(cli_list) + len(sw_list)

def get_matrix_from_network_csv(csv_filename, size):
    matrix = [[INFTY] * size for i in range(size)]

    df = pd.read_csv(csv_filename)
    for row in df.itertuples():
        nodeFrom = row.nodeFrom
        nodeTo = row.nodeTo
        cost = row.cost
        matrix[nodeFrom][nodeTo] = cost
        matrix[nodeTo][nodeFrom] = cost

    return matrix

def main(i_srcNode, i_dstNode):
    home_dir = os.path.expanduser('~')
    size = get_size_from_node_csv('{}/workspace/test_z3/network/network/node.csv'.format(home_dir))
    matrix = get_matrix_from_network_csv('{}/workspace/test_z3/network/network/network.csv'.format(home_dir), size)

    path = get_path_using_dijkstra(matrix, i_srcNode, i_dstNode)

    return path


if __name__ == "__main__":
    main(7, 4)