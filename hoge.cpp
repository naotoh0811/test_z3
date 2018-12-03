//https://stackoverflow.com/questions/30596915/how-to-use-z3-c-api-to-solve-array-theory
#include"z3++.h"

using namespace z3;

void find_model_example(int x_min) {
    context c;
    unsigned i=0,j;
    expr_vector T(c);
    solver s(c);

    for(; i<20; i++){
        std::stringstream Tname;
        Tname<<"Tname_"<<i;
        T.push_back(c.int_const(Tname.str().c_str()));
    }

    for(i=0; i<20; i++){
        for(j=0; j<20;j++){
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
