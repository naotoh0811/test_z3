#include<iostream>
#include<fstream>
#include "z3++.h"
#include "func.h"

using namespace z3;

void find_model_example() {
    std::cout << "find_model_example1\n";
    context c;
    expr_vector optime(c);
    expr_vector cltime(c);
    expr_vector que(c);
    expr x = c.int_const("x");
    solver s(c);

    // request
    int ocu_time = 2;
    int cycle_time[] = {20, 30, 40};

    // various variables
    int num_flow; // the number of all flows
    num_flow = sizeof(cycle_time) / sizeof(*cycle_time);

    int schedule_cycle; // one cycle time of schedule
    schedule_cycle = multi_lcm(cycle_time, num_flow);

    int num_win = 0; // the number of all windows
    int i_win_first[num_flow]; // index of first window of each flow
    int i_win_last[num_flow]; // index of last window of each flow
    int each_num_win = 0;
    for(int i = 0; i < num_flow; i++){
        i_win_first[i] = num_win;
        num_win += schedule_cycle / cycle_time[i];
        i_win_last[i] = num_win - 1;
    }

    // define vector
    for(int i = 0; i < num_win; i++){
        std::stringstream optime_name, cltime_name, que_name;
        optime_name << "optime_" << i;
        cltime_name << "cltime_" << i;
        que_name << "que_" << i;
        optime.push_back(c.int_const(optime_name.str().c_str()));
        cltime.push_back(c.int_const(cltime_name.str().c_str()));
        que.push_back(c.int_const(que_name.str().c_str()));
    }

    /********** Constraint **********/

    // flow cycle
    for(int i = 0; i < num_flow; i++){
        for(int j = i_win_first[i]; j < i_win_last[i] + 1; j++){
            if(j != i_win_last[i]){
                s.add(optime[j+1] - optime[j] == cycle_time[i]);
            }else{
                s.add( (schedule_cycle - optime[j]) + (optime[i_win_first[i]] - 0) == cycle_time[i] );
            }
        }
    }

    // exclusiveness
    for(int i = 0; i < num_win; i++){
        for(int j = 0; j < num_win; j++){
            if(i != j){
                s.add(cltime[i] < optime[j] || cltime[i] > cltime[j]);
            }
        }
    }

    // occupancy time
    for(int i = 0; i < num_win; i++){
        s.add(cltime[i] - optime[i] == ocu_time);
    }

    // range of schedule cycle
    for(int i = 0; i < num_win; i++){
        s.add(optime[i] >= 0);
        s.add(cltime[i] <= schedule_cycle);
    }

    /********************************/

    std::cout << "-----sat check-----" << "\n"; 
    std::cout << s.check() << "\n";
    std::cout << "-------------------" << "\n"; 

    model m = s.get_model();
    //std::cout << "-----model m-----" << "\n"; 
    //std::cout << m << "\n";
    //std::cout << "-----------------" << "\n"; 

    std::cout << "schedule cycle time = " << schedule_cycle << "\n";

    std::ofstream out("hoge.txt");

    out << "{";
    for(int i = 0; i < num_flow; i++){
        out << "{";
        out << "\"flow" << i << "\":{";
        out << "\"cycle\":" << cycle_time[i] << ",";
        out << "\"time\":[";
        for(int j = i_win_first[i]; j <  i_win_last[i] + 1; j++){
            out << "[" << m.eval(optime[j]) << "," << m.eval(cltime[j]) << "],";
        }
        out << "]";
        out << "},";
    }
    out << "}";
    
    out.close();

    for(int i = 0; i < num_flow; i++){
        std::cout << "#cycle:" << cycle_time[i] << "\n";
        for(int j = i_win_first[i]; j < i_win_last[i] + 1; j++){
            std::cout << m.eval(optime[j]) << ",";
            std::cout << m.eval(cltime[j]) << "\n";
        }
        //std::cout << "\n";
    }
}


int main(int argc, char *argv[]) {
    int arg = 10;
    if (argc > 1) arg = atoi(argv[1]);
    try {
        find_model_example();
        std::cout << "\n";
        std::cout << "done\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }
    return 0;
}

