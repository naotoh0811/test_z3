#include "z3++.h"
#include "func.h"

using namespace z3;


void find_model_example(int x_min) {
    std::cout << "find_model_example1\n";
    context c;
    expr_vector optime(c);
    expr_vector cltime(c);
    expr_vector que(c);
    //expr_vector win(c);
    expr x = c.int_const("x");
    solver s(c);
    int num_flow = 10;
    int win[2][4] = {};
    int cycle_time[2] = {};

    for(int i = 0; i < 10; i++){
        std::stringstream optime_name, cltime_name, que_name;
        optime_name << "optime_" << i;
        cltime_name << "cltime_" << i;
        que_name << "que_" << i;
        optime.push_back(c.int_const(optime_name.str().c_str()));
        cltime.push_back(c.int_const(cltime_name.str().c_str()));
        que.push_back(c.int_const(que_name.str().c_str()));
    }

    //s.add(optime[1] == 100);

    /*s.add(win[0] == 0);
    s.add(win[1] == 2);
    s.add(win[2] == 3);
    s.add(win[3] == 5);
    s.add(win[4] == 1);
    s.add(win[5] == 4);*/
    win[0][0] = 0;
    win[0][1] = 2;
    win[0][2] = 3;
    win[0][3] = 5;
    win[1][0] = 1;
    win[1][1] = 4;
    cycle_time[0] = 20;
    cycle_time[1] = 30;

    //周期を守る
    for(int i = 0; i < 4 - 1; i++){
        s.add(optime[win[0][i + 1]] - optime[win[0][i]] == cycle_time[0]);
    }
    for(int i = 0; i < 2 - 1; i++){
        s.add(optime[win[1][i + 1]] - optime[win[1][i]] == cycle_time[1]);
    }

    //排他性
    for(int i = 0; i < 6 - 1; i++){
        s.add(cltime[i] <= optime[i + 1]);
    }

    //長さ
    for(int i = 0; i < 6; i++){
        s.add(cltime[i] - optime[i] == 1);
    }

    //範囲
    for(int i = 0; i < 6; i++){
        s.add(optime[i] >= 0);
        s.add(cltime[i] <= 400);
    }
    s.add(optime[0] == 0);

    std::cout << s.check() << "\n";

    std::cout << "--solver s--\n" << s << "\n";

    model m = s.get_model();
    std::cout << "--model m--\n" << m << "\n";
    // traversing the model
    std::cout << "\n--results--\n";
    /*for (int i = 0; i < m.size(); i++) {
        func_decl v = m[i];
        // this problem contains only constants
        assert(v.arity() == 0); 
        std::cout << v.name() << " = " << m.get_const_interp(v) << "\n";
    }*/
    for(int i = 0; i < 6; i++){
        std::cout << "optime_" << i << " = " << m.eval(optime[i]) << " ";
        std::cout << "cltime_" << i << " = " << m.eval(cltime[i]) << "\n";
    }
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
    //int hog[]={3,4,5,8};
    //std::cout << multi_lcm(hog, 4) << "\n";
    return 0;
}