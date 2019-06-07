#include <iostream>
#include <fstream>
#include "z3++.h"
#include "../func.h"

using namespace z3;

void find_model_example(int i_sw, int *cycle_time, int num_flow, int ocu_time) {
    context c;
    expr_vector optime(c);
    expr_vector cltime(c);
    expr_vector que(c);
    expr x = c.int_const("x");
    solver s(c);

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
                s.add(cltime[i] <= optime[j] || optime[i] >= cltime[j]);
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

    // make yaml file
    std::string yaml_filename = "schedule" + std::to_string(i_sw) + ".yml";
    std::ofstream out(yaml_filename);
    out << "num_flow : " << num_flow << "\n";
    out << "schedule_cycle: " << schedule_cycle << "\n";
    out << "flow:\n";
    for(int i = 0; i < num_flow; i++){
        out << "  - name: flow" << i << "\n";
        out << "    cycle: " << cycle_time[i] << "\n";
        out << "    time:\n";
        for(int j = i_win_first[i]; j <  i_win_last[i] + 1; j++){
            out << "      - [" << m.eval(optime[j]) << "," << m.eval(cltime[j]) << "]\n";
        }
    }
    out.close();

    std::cout << "schedule cycle time = " << schedule_cycle << "\n";
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
    int cycle_time1[] = {20, 30, 40, 60};
    int cycle_time2[] = {20, 50};
    int num_flow1 = sizeof(cycle_time1) / sizeof(*cycle_time1);
    int num_flow2 = sizeof(cycle_time2) / sizeof(*cycle_time2);
    try {
        find_model_example(1, cycle_time1, num_flow1, 3);
        std::cout << "\n";
        std::cout << "done\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }

    try {
        find_model_example(2, cycle_time2, num_flow2, 3);
        std::cout << "\n";
        std::cout << "done\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }
    return 0;
}

