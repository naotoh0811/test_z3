#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <cstdlib>
using namespace std;

// http://katsura-kotonoha.sakura.ne.jp/prog/c/tip0000a.shtml
int gcd(int m, int n){
	// 引数に０がある場合は０を返す
	if( ( 0 == m ) || ( 0 == n ) ) return 0;
	
	// ユークリッドの方法
	while(m != n){
		if(m > n) m = m - n;
		else n = n - m;
	}
	return m;
}

int lcm( int m, int n ){
	// 引数に０がある場合は０を返す
	if( ( 0 == m ) || ( 0 == n ) ) return 0;
	
	return ((m / gcd(m, n)) * n); // lcm = m * n / gcd(m,n)
}

int multi_lcm(int *num, int size){
	int tmp = num[0];
	for(int i = 1; i < size; i++){
		tmp = lcm(tmp, num[i]);
	}
	return tmp;
}

// https://www.sejuku.net/blog/49378#find_first_of
vector<string> split(string str, char del) {
    int first = 0;
    int last = str.find_first_of(del);
 
    vector<string> result;
 
    while (first < str.size()) {
        string subStr(str, first, last - first);
 
        result.push_back(subStr);
 
        first = last + 1;
        last = str.find_first_of(del, first);
 
        if (last == string::npos) {
            last = str.size();
        }
    }
 
    return result;
}

int get_size(ifstream &ifs){
    string str;

	getline(ifs, str);
    vector<string> result = split(str, ',');

	return atoi(result[3].c_str());
}

struct network_status{
	int nodeFrom;
	int nodeTo;
	int cost;
	
	network_status(int nf, int nt, int c){
		nodeFrom = nf;
		nodeTo = nt;
		cost = c;
	}
};

vector<network_status> set_matrix_from_csv(int **matrix, ifstream &ifs){
    string str;
    vector<string> result;
	vector<network_status> ns_vec;
    while(getline(ifs, str)){
        result = split(str, ',');

        int nodeFrom = atoi(result[0].c_str());
        int nodeTo = atoi(result[1].c_str());
        int cost = atoi(result[2].c_str());

		ns_vec.push_back(network_status(nodeFrom, nodeTo, cost));

        //matrix[nodeFrom][nodeTo] = cost;
        //matrix[nodeTo][nodeFrom] = cost;

    }
	return ns_vec;
}

void set_matrix(int **matrix, vector<network_status> ns_vec, int size){
	for(auto itr : ns_vec){
		matrix[itr.nodeFrom][itr.nodeTo] = itr.cost;		
	}
}