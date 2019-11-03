//https://stackoverflow.com/questions/30596915/how-to-use-z3-c-api-to-solve-array-theory
#include"z3++.h"
# include <vector>

using namespace z3;

void find_model_example(int x_min) {
    context c;
    expr_vector T(c);
    solver s(c);

    std::vector<expr_vector> hoge;
    hoge.push_back(expr_vector(c));
    hoge[0].push_back(c.int_const("hoge0_0"));
    hoge[0].push_back(c.int_const("hoge0_1"));
    s.add(hoge[0][0] == 10);

    for(int i = 0; i<20; i++){
        std::stringstream Tname;
        Tname<<"Tname_"<<i;
        T.push_back(c.int_const(Tname.str().c_str()));
    }

    for(int i=0; i<20; i++){
        for(int j=0; j<20;j++){
            if(j == i){
                s.add(T[i] != T[j]);
            }
        }
    }
    std::cout<<s<<"\n"<<s.check()<<std::endl;
}

int main(int argc, char *argv[]) {
	int arg = 10;
	if (argc > 1) arg = atoi(argv[1]);
    try {
        find_model_example(arg);
		std::cout << "\n";
        std::cout << "done\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }
    return 0;
}
