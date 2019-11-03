#include <iostream>
#include <fstream>
#include "z3++.h"

using namespace z3;


int calc(int a){
	return a*2;
}

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

	int a = 1;
	//opt.add(x == a);
    opt.add(x == calc(a)); //calc(x)はcalc(1)とみなされる
    //opt.add(x <= 10);
    opt.add(y <= 10);
    opt.add(z <= 10);
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
		break;
        }
        else {
			std::cout << "unsat" << "\n";
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

