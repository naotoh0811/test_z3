// https://algorithmbeginner.blogspot.com/2018/02/blog-post_21.html
#include <iostream>
#include <stdio.h>
#include <string>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <vector>
#include "../func.h"
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
    int size = 8;
    int startNode_index = 0;
    
    for(int i = 0; i < size; ++i){
        for(int j = 0; j < size; ++j){
            gMatrix[i][j] = INFTY;
        }
    }

    ifstream ifs("network.csv");
    string str;
    vector<string> result;
    
    // ignore first line
    getline(ifs, str);

    while(getline(ifs, str)){
        result = split(str, ',');
        int nodeFrom = atoi(result[0].c_str());
        int nodeTo = atoi(result[1].c_str());
        int cost = atoi(result[2].c_str());
        gMatrix[nodeFrom][nodeTo] = cost;
        gMatrix[nodeTo][nodeFrom] = cost;
    }

    dijkstra(size, startNode_index);
    return 0;
}