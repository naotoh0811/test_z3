#include"z3++.h"

using namespace z3;


void find_model_example(int x_min) {
    std::cout << "find_model_example1\n";
    context c;
    expr x = c.int_const("xxx");

    sort I = c.int_sort();
    sort A = c.array_sort(I, I);
    expr a1 = c.constant("a1", A);
    //expr a1 = to_expr(c, mk_var(c, "a1", A));
    //expr b1 = store(a1, 3, 4);
    expr ITE = select(a1, 0);
    expr b1 = select(a1, 1000);
    expr b2 = select(a1, 2000);
    expr b3 = select(a1, 3000);
    solver s(c);

    s.add(ITE == 100);
    s.add(b1 == 101);
    s.add(b2 == 102);
    s.add(b3 == 103);
    s.add(x == 1);
    std::cout << s.check() << "\n" << "-------" << "\n";

    std::cout << s << "\n" << "-------" << "\n";

    model m = s.get_model();
    std::cout << m << "\n" << "-------" << "\n";
    // traversing the model
    for (unsigned i = 0; i < m.size(); i++) {
        func_decl v = m[i];
        // this problem contains only constants
        assert(v.arity() == 0); 
        std::cout << v.name() << " = " << m.get_const_interp(v) << "\n";
    }
    // we can evaluate expressions in the model.
    //std::cout << "x + y + 1 = " << m.eval(x + y + 1) << "\n";
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
