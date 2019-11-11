import sys
import os.path
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import network.network.gen_linear_network as gen_linear_network
import network.flow.gen_flow_using_network_csv as gen_flow_using_network_csv
import network.dijkstra.gen_flowData as gen_flowData
import multiSw_sch.sch as sch
import subprocess

def from_gen_network_to_sch(num_sw, num_flow):
    print(1)
    gen_linear_network.main(num_sw)
    print(2)
    gen_flow_using_network_csv.main(num_flow)
    print(3)
    gen_flowData.main()
    print(4)
    sch.main()

def main():
    from_gen_network_to_sch(3, 3)

if __name__ == "__main__":
    main()