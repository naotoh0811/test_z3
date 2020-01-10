import os.path
import sys
import random
import time
import itertools
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.explore_max_value as explore_max_value

def get_result_list(max_num_flow):
    result_list = []
    for num_flow in range(2, max_num_flow + 1):
        # generate dammy flow
        flow_list = gen_dammy_flow_list(num_flow)

        # get hist list
        hist_and_priority_dic_list, flow_prio_list = explore_max_value.get_hist_list_from_flow_list(flow_list, for_measure=True)

        # sort list by priority
        # list index is equal to priority
        hist_and_priority_dic_list = sorted(hist_and_priority_dic_list, reverse=False, key=lambda x:x["priority"])

        # get permutation list
        prio_permutation_list = list(itertools.permutations(flow_prio_list))

        # explore max value
        start_time = time.time()
        max_sum_expected_value, max_prio_permutation_list = \
            explore_max_value.explore_max_value_from_lists(flow_list, hist_and_priority_dic_list, prio_permutation_list)
        elapsed_time = time.time() - start_time

        result_list.append(elapsed_time)
        print(num_flow, elapsed_time)

    return result_list


def gen_dammy_flow_list(num_flow):
    dammy_flow_list = []
    for i in range(num_flow):
        flow_dic = { \
            "flow_id": random.randint(0, 6), \
            "tuf": [[0, 19.596, "linear", 0, 100], [19.596, 55.596, "linear", -2.778, 154.4]] \
        }
        dammy_flow_list.append(flow_dic)

    return dammy_flow_list

def gen_result_graph(result_list, max_num_flow):
    # generate num_flow list
    num_flow_list = range(2, max_num_flow + 1)

    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    fig, ax = plt.subplots()

    # plot
    p = ax.plot(num_flow_list, result_list, marker=".", c='b')

    # set scale
    ax.set_yscale('log')

    # set label
    ax.set_xlabel('Number of soft real-time flows')
    ax.set_ylabel('Calculation time [s]')

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('{}/workspace/test_z3/multiSw_sch/pdf/num_flow_vs_time.pdf'.format(home_dir))

def make_pdf(pdf_filename):
    pp = PdfPages(pdf_filename)
    pp.savefig()
    pp.close()
    plt.clf()

def main():
    max_num_flow = 10

    # get result list
    # result_list = get_result_list(max_num_flow)
    # result_list = [0.0001277923583984375, 0.0004677772521972656, 0.0019385814666748047, 0.012128591537475586, 0.08089661598205566, 0.69547438621521, 5.672691822052002, 59.926318883895874]
    result_list = [0.00006389, 0.00021, 0.0079, 0.054, 0.39, 3.54, 35.62, 438, 4919]

    # generate graph
    gen_result_graph(result_list, max_num_flow)


if __name__ == "__main__":
    main()
