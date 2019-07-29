// https://algorithmbeginner.blogspot.com/2018/02/blog-post_21.html
#include <iostream>
using namespace std;
#define MAX 100
#define INFTY 1<<22
#define WHITE 0
#define GRAY 1
#define BLACK 2

int gMatrix[MAX][MAX];

void dijkstra(int size, int startNode_index){
    // 最小の重みを記録する
    int minV;
    // weight[adjNode_index]に始点sからvまでの最短コストを保存する
    int weight[MAX];
    // 訪問状態を記録
    int color[MAX];
    // 1.初期化
    for(int i = 0;i < size;++i){
        weight[i] = INFTY;
        color[i] = WHITE;
    }
    // 始点
    weight[startNode_index] = 0;
    color[startNode_index] = GRAY;
    
    while(1){
        minV = INFTY;
        // 頂点を示す
        int minNode_index = -1;
        // 2.1weight[minNode_index]が最小である頂点を決定する
        for(int i = 0;i < size;++i){
            if(minV > weight[i] && color[i] != BLACK){
                minNode_index = i;
                minV = weight[i];
            }
        }
        if(minNode_index == -1)break;
        color[minNode_index] = BLACK;
        
        for(int adjNode_index = 0;adjNode_index < size;++adjNode_index){
            // 辺が存在する
            if(color[adjNode_index] != BLACK && gMatrix[minNode_index][adjNode_index] != INFTY){
                // 2.2最短コストを更新する
                // この処理の終了後weight[adjNode_index]sからS内の頂点のみを経由したvまでの最短コストが記録される
                if(weight[adjNode_index] > weight[minNode_index] + gMatrix[minNode_index][adjNode_index]){
                    weight[adjNode_index] = weight[minNode_index] + gMatrix[minNode_index][adjNode_index];
                    color[adjNode_index] = GRAY;
                }
            }
        }
    }
    // 出力
    for(int i = 0;i < size;++i){
        cout << "node" << startNode_index << " to node" << i << " " << ( weight[i] == INFTY ? -1 : weight[i] ) << endl;
    }
}

int main(){
    int size = 4;
    int startNode_index = 0;
    
    for(int i = 0;i < size;++i){
        for(int j = 0;j < size;++j){
            gMatrix[i][j] = INFTY;
        }
    }

    gMatrix[0][3] = 1;
    gMatrix[1][3] = 1;
    gMatrix[2][3] = 1;
    gMatrix[3][0] = 1;
    gMatrix[3][1] = 1;
    gMatrix[3][2] = 1;

    dijkstra(size, startNode_index);
    return 0;
}