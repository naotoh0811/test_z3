import sys
import os.path
import subprocess
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import network.network.gen_linear_network as gen_linear_network
import network.flow.gen_flow_using_network_csv as gen_flow_using_network_csv
import network.dijkstra.gen_flowData as gen_flowData
import multiSw_sch.sch as sch

NOT_DEFINE = 1000
UNSAT = 1
SAT = 0

def from_gen_network_to_sch(num_sw, num_flow):
    gen_linear_network.main(num_sw)
    gen_flow_using_network_csv.main(num_flow)
    gen_flowData.main()
    sat_or_unsat = sch.main()

    return sat_or_unsat

def main():
    cnt_sat = 0
    cnt_unsat = 0
    for i in range(100):
        sat_or_unsat = from_gen_network_to_sch(3, 3)
        if sat_or_unsat == SAT:
            cnt_sat += 1
        else:
            cnt_unsat += 1
    print(cnt_sat, cnt_unsat)



if __name__ == "__main__":
    main()