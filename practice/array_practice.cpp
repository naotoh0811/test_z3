#include"z3++.h"

using namespace z3;


void array_pra() {
    context c;
    expr x(c);
    expr y(c);
    expr_vector hoge(c);
    x = c.int_const("X");
    y = c.int_const("Y");
    //hoge[1] = c.int_const("hoge0");
    hoge.push_back(c.int_const("hoge0"));
    hoge.push_back(c.int_const("hoge1"));
    hoge.push_back(c.int_const("hoge2"));
    hoge.push_back(c.int_const("hoge3"));
    solver s(c);

    s.add(x == 2);
    //s.add(y < x + 3);
    //s.add(hoge[0] == 100);
    //s.add(hoge[1] == 101);
    int v;
    s.add(hoge[v] == 9);
    //s.add(hoge[1] == 8);
    //s.add(hoge[0] == 2);

    std::cout << "-----sat check-----" << "\n"; 
    std::cout << s.check() << "\n";
    std::cout << "-------------------" << "\n"; 

    model m = s.get_model();
    std::cout << "-----model m-----" << "\n"; 
    std::cout << m << "\n";
    std::cout << "-----------------" << "\n"; 

    // traversing the model
    for (unsigned i = 0; i < m.size(); i++) {
        func_decl v = m[i];
        // this problem contains only constants
        assert(v.arity() == 0); 
        std::cout << v.name() << " = " << m.get_const_interp(v) << "\n";
    }
}


int main(int argc, char *argv[]) {
	int arg = 10;
	if (argc > 1) arg = atoi(argv[1]);
    try {
        array_pra();
		std::cout << "\n";
        std::cout << "done\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }
    return 0;
}
