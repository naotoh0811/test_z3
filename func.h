#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <cstdlib>
// for all_of
#include <cctype>
#include <algorithm>
//using namespace std;

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
std::vector<std::string> split(std::string str, char del) {
    int first = 0;
    int last = str.find_first_of(del);
 
    std::vector<std::string> result;
 
    while (first < str.size()) {
        std::string subStr(str, first, last - first);
 
        result.push_back(subStr);
 
        first = last + 1;
        last = str.find_first_of(del, first);
 
        if (last == std::string::npos) {
            last = str.size();
        }
    }
 
    return result;
}

int get_size(std::ifstream &ifs){
    std::string str;

	getline(ifs, str);
    std::vector<std::string> result = split(str, ',');

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

bool check_int(std::string str)
{
    if (std::all_of(str.cbegin(), str.cend(), isdigit)) return true;
    else return false;
}

std::vector<network_status> csv_to_status(int **matrix, std::ifstream &ifs){
    std::string str;
    std::vector<std::string> result;
	std::vector<network_status> ns_vec;
    while(getline(ifs, str)){
        result = split(str, ',');

		if(!check_int(result[0])) continue;

        int nodeFrom = atoi(result[0].c_str());
        int nodeTo = atoi(result[1].c_str());
        int cost = atoi(result[2].c_str());

		ns_vec.push_back(network_status(nodeFrom, nodeTo, cost));
    }
	return ns_vec;
}

void set_matrix(int **matrix, std::vector<network_status> ns_vec){
	for(auto itr : ns_vec){
		matrix[itr.nodeFrom][itr.nodeTo] = itr.cost;
		matrix[itr.nodeTo][itr.nodeFrom] = itr.cost;
	}
}