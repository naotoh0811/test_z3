// https://algorithmbeginner.blogspot.com/2018/02/blog-post_21.html
#include <iostream>
#include "dj_func.h"
using namespace std;
#define INFTY 1<<22
#define WHITE 0 // unfixed
#define BLACK 1 // fixed


void dijkstra(int **matrix, int size, int startNode_index){
    // minimum cost
    int minCost;
    // cost from startNode
    int cost[size];
    // fixed or unfixed
    int color[size];
    // passed prevNode
    int prevNode[size];
    
    // initialize
    for(int i = 0;i < size;++i){
        cost[i] = INFTY;
        color[i] = WHITE;
        prevNode[i] = -1;
    }

    // startNode
    cost[startNode_index] = 0;
    prevNode[startNode_index] = startNode_index;

    while(1){
        minCost = INFTY;
        int minNode_index = -1;
        // search node which has minimum cost
        for(int i = 0;i < size;++i){
            if(minCost > cost[i] && color[i] != BLACK){
                minNode_index = i;
                minCost = cost[i];
            }
        }
        if(minNode_index == -1)break;
        color[minNode_index] = BLACK;
        
        for(int adjNode_index = 0; adjNode_index < size; ++adjNode_index){
            if(color[adjNode_index] != BLACK && matrix[minNode_index][adjNode_index] != INFTY){
                // update cost and prevNode
                if(cost[adjNode_index] > cost[minNode_index] + matrix[minNode_index][adjNode_index]){
                    cost[adjNode_index] = cost[minNode_index] + matrix[minNode_index][adjNode_index];
                    prevNode[adjNode_index] = minNode_index;
                }
            }
        }
    }

    // result output
    for(int i = 0;i < size;++i){
        // distance
        cout << "node" << startNode_index << " to node" << i
             << " : distance = " << ( cost[i] == INFTY ? -1 : cost[i] ) << endl;

        // path
        int prevprevNode = prevNode[i];
        cout << i << " <- ";
        while(prevprevNode != startNode_index){
            cout << prevprevNode << " <- ";
            prevprevNode = prevNode[prevprevNode];
        }
        cout << prevprevNode << endl;
    }
}

int main(){
    ifstream ifs("network.csv");

    // read status from csv
    vector<network_status> ns_vec;
    ns_vec = csv_to_status(ifs);

    // set size
    int size = get_size(ns_vec);

    // initialize matrix
    int gMatrix[size][size];
    for(int i = 0; i < size; ++i){
        for(int j = 0; j < size; ++j){
            gMatrix[i][j] = INFTY;
        }
    }

    // prepare for arg
    int *matrix_arg[size];
    for (int i = 0; i < size; i++) matrix_arg[i] = gMatrix[i];

    //set cost
    set_matrix(matrix_arg, ns_vec);

    int startNode_index = 0;

    dijkstra(matrix_arg, size, startNode_index);

    return 0;
}