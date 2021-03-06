#include <iostream>
#include <string>
#include <vector>
#include <fstream>
#include <cstdlib>
// for all_of
#include <cctype>
#include <algorithm>

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

std::vector<network_status> csv_to_status(std::ifstream &ifs){
    std::string str;
    std::vector<std::string> result;
	std::vector<network_status> ns_vec;
    while(getline(ifs, str)){
        result = split(str, ',');

		// skip header
		if(!check_int(result[2])) continue;

        int nodeFrom = atoi(result[0].c_str());
        int nodeTo = atoi(result[1].c_str());
        int cost = atoi(result[2].c_str());

		ns_vec.push_back(network_status(nodeFrom, nodeTo, cost));
    }
	return ns_vec;
}

int get_size(std::vector<network_status> ns_vec){
	std::vector<int> nodes;
	for(auto itr : ns_vec){
		nodes.push_back(itr.nodeFrom);
		nodes.push_back(itr.nodeTo);
	}
	std::sort(nodes.begin(), nodes.end());
	nodes.erase(std::unique(nodes.begin(), nodes.end()), nodes.end());

	return nodes.size();
}

void set_matrix(int **matrix, std::vector<network_status> ns_vec){
	for(auto itr : ns_vec){
		matrix[itr.nodeFrom][itr.nodeTo] = itr.cost;
		matrix[itr.nodeTo][itr.nodeFrom] = itr.cost;
	}
}