// https://algorithmbeginner.blogspot.com/2018/02/blog-post_21.html
#include <iostream>
using namespace std;
#define MAX 100
#define INFTY 1<<22
#define WHITE 0 // unfixed
#define BLACK 1 // fixed

int gMatrix[MAX][MAX];

void dijkstra(int size, int startNode_index){
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
            if(color[adjNode_index] != BLACK && gMatrix[minNode_index][adjNode_index] != INFTY){
                // update cost and prevNode
                if(cost[adjNode_index] > cost[minNode_index] + gMatrix[minNode_index][adjNode_index]){
                    cost[adjNode_index] = cost[minNode_index] + gMatrix[minNode_index][adjNode_index];
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

        // all passed nodes
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
    int size = 5;
    int startNode_index = 0;
    
    for(int i = 0;i < size;++i){
        for(int j = 0;j < size;++j){
            gMatrix[i][j] = INFTY;
        }
    }

    gMatrix[0][1] = 1;
    gMatrix[0][2] = 2;
    gMatrix[0][3] = 1;
    gMatrix[1][0] = 1;
    gMatrix[1][4] = 2;
    gMatrix[2][0] = 2;
    gMatrix[2][3] = 1;
    gMatrix[2][4] = 3;
    gMatrix[3][0] = 1;
    gMatrix[3][2] = 1;
    gMatrix[4][1] = 2;
    gMatrix[4][2] = 3;

    dijkstra(size, startNode_index);
    return 0;
}