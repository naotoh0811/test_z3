#include"z3++.h"

using namespace z3;


void find_model_example(int x_min) {
    std::cout << "find_model_example1\n";
    context c;
    expr x = c.int_const("x");
    expr y = c.int_const("y");
    solver s(c);

    s.add(x >= x_min);
    s.add(y < x + 3);
    std::cout << s.check() << "\n";

    model m = s.get_model();
    std::cout << m << "\n";
    // traversing the model
    for (unsigned i = 0; i < m.size(); i++) {
        func_decl v = m[i];
        // this problem contains only constants
        assert(v.arity() == 0); 
        std::cout << v.name() << " = " << m.get_const_interp(v) << "\n";
    }
    // we can evaluate expressions in the model.
    std::cout << "x + y + 1 = " << m.eval(x + y + 1) << "\n";
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
