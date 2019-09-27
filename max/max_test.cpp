#include <iostream>
#include <fstream>
#include "z3++.h"

using namespace z3;


void opt_example() {
    context c;
    optimize opt(c);
    params p(c);
    p.set("priority",c.str_symbol("pareto"));
    opt.set(p);

    expr x = c.int_const("x");
    expr y = c.int_const("y");
    expr z = c.int_const("z");
    expr_vector hoge(c);
    hoge.push_back(c.int_const("hoge0"));
    hoge.push_back(c.int_const("hoge1"));

    opt.add(2 * x <= 4);
    opt.add(x + 2 * z <= 8);
    opt.add(3 * y + z <= 6);
    opt.add(x >= 0);
    opt.add(y >= 0);
    opt.add(z >= 0);
    opt.add(hoge[0] == 0);
    optimize::handle h1 = opt.maximize(3 * x + 4 * y + 2 * z);
    
    while (true) {
        if (sat == opt.check()) {
            std::cout << "max : " << opt.lower(h1) << "\n";
            model m = opt.get_model();
            for(int i = 0; i < m.size(); i++){
                func_decl v = m[i];
                std::cout << v.name() << " = " << m.get_const_interp(v) << "\n";
            }
        }
        else {
            break;
        }
    }
}


int main(int argc, char *argv[]) {
    try {
        opt_example(); std::cout << "\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }
    return 0;
}

