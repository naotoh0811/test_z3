import sys
import os.path
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import network.network.gen_linear_network as gen_linear_network
import network.flow.gen_flow_using_network_csv as gen_flow_using_network_csv
import network.dijkstra.gen_flowData as gen_flowData
import multiSw_sch.sch as sch


def main(num_sw, num_flow, num_flow_soft):
    gen_linear_network.main(num_sw)
    gen_flow_using_network_csv.main(num_flow, num_flow_soft)
    gen_flowData.main()

if __name__ == "__main__":
    num_sw = 5
    num_flow = 5
    num_flow_soft = 3
    if len(sys.argv) == 4:
        num_sw = int(sys.argv[1])
        num_flow = int(sys.argv[2])
        num_flow_soft = int(sys.argv[3])
    else:
        print("WARNING: arg is invalid. Now set num_sw to 5, num_flow to 5, num_flow_soft to 3.")

    main(num_sw, num_flow, num_flow_soft)