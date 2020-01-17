import os.path
import sys
import random
import time
import itertools
import numpy as np
from statistics import mean
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.explore_max_value as explore_max_value
import multiSw_sch.gen_network_and_flow as gen_network_and_flow
import multiSw_sch.sch as sch
import multiSw_sch.sch_with_soft as sch_with_soft

UNSAT = -2
SAT = -1


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

def gen_time_graph_for_soft(result_list, max_num_flow):
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

    # set grid
    ax.grid()

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('{}/workspace/test_z3/multiSw_sch/pdf/num_soft_flow_vs_time.pdf'.format(home_dir))

def gen_time_graph_for_hard_errorbar(x, y, y_err):
    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    fig, ax = plt.subplots()

    # plot
    ax.errorbar(x, y, yerr=y_err, fmt='b.-')

    # set label
    ax.set_xlabel('Number of hard real-time flows')
    ax.set_ylabel('Calculation time [s]')

    # set ticks
    max_num_flow_hard = x[-1]
    ax.set_xticks(range(1, max_num_flow_hard + 1))

    # set lim
    ax.set_ylim(0,)

    # set grid
    ax.grid()

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('{}/workspace/test_z3/multiSw_sch/pdf/num_hard_flow_vs_time.pdf'.format(home_dir))

def gen_time_graph_for_hard_boxplot(num_flow_hard_list, elapsed_time_list_list):
    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    fig, ax = plt.subplots()

    # plot
    ax.boxplot(elapsed_time_list_list, labels=num_flow_hard_list, patch_artist=True, \
        boxprops={'facecolor': 'lightblue'})

    # set label
    ax.set_xlabel('Number of hard real-time flows')
    ax.set_ylabel('Calculation time [s]')

    # set ticks
    max_num_flow_hard = num_flow_hard_list[-1]
    ax.set_xticks(range(1, max_num_flow_hard + 1))

    # set lim
    ax.set_ylim(0,)

    # set grid
    ax.grid()

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('{}/workspace/test_z3/multiSw_sch/pdf/num_hard_flow_vs_time.pdf'.format(home_dir))

def gen_rate_graph(num_flow_hard_list, sat_rate_list):
    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    fig, ax = plt.subplots()

    # plot
    ax.plot(num_flow_hard_list, sat_rate_list, marker='.', c='b')

    # set label
    ax.set_xlabel('Number of hard real-time flows')
    ax.set_ylabel('Scheduling success rate [%]')

    # set ticks
    max_num_flow_hard = num_flow_hard_list[-1]
    ax.set_xticks(range(1, max_num_flow_hard + 1))

    # set lim
    ax.set_ylim(0,100)

    # set grid
    ax.grid()

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('{}/workspace/test_z3/multiSw_sch/pdf/num_hard_flow_vs_rate.pdf'.format(home_dir))

def make_pdf(pdf_filename):
    pp = PdfPages(pdf_filename)
    pp.savefig()
    pp.close()
    plt.clf()

def measure_time_for_soft():
    max_num_flow = 10

    # get result list
    # result_list = get_result_list(max_num_flow)
    # result_list = [0.0001277923583984375, 0.0004677772521972656, 0.0019385814666748047, 0.012128591537475586, 0.08089661598205566, 0.69547438621521, 5.672691822052002, 59.926318883895874]
    result_list = [0.00006389, 0.00021, 0.0079, 0.054, 0.39, 3.54, 35.62, 438, 4919]

    # generate graph
    gen_time_graph_for_soft(result_list, max_num_flow)

def measure_time_for_hard():
    max_num_flow_hard = 7
    num_flow_hard_list = range(1, max_num_flow_hard + 1)
    # for errorbar
    mean_elapsed_time_list = []
    upper_err_list = []
    lower_err_list = []
    # for boxplot
    elapsed_time_list_list = []
    # for rate
    sat_rate_list = []

    for num_flow_hard in num_flow_hard_list:
        sat_count = 0
        unsat_count = 0
        elapsed_time_list = []
        for i in range(20):
            # generate network and flow
            num_sw = 5
            num_cli_for_each_sw = num_flow_hard
            num_flow = num_flow_hard
            num_flow_soft = 0
            num_pass_sw = 5
            fixed_bandwidth = 900
            cycle_soft = 50
            gen_network_and_flow.main( \
                num_sw, num_cli_for_each_sw, num_flow, num_flow_soft, num_pass_sw, fixed_bandwidth, cycle_soft \
            )

            # get list
            flow_with_path_hard_filename = \
                '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir)
            flow_list_hard, _, _, _ = sch_with_soft.check_existence_and_get_flow_list( \
                flow_with_path_hard_filename, '')

            # measure scheduling time
            start_time = time.time()
            sat_or_unsat = sch.main(flow_list_hard)
            elapsed_time = time.time() - start_time

            # count SAT/UNSAT
            if sat_or_unsat == SAT:
                sat_count += 1
                print(num_flow_hard, 'SAT', elapsed_time)
                elapsed_time_list.append(elapsed_time)
            else:
                unsat_count += 1
                print(num_flow_hard, 'UNSAT')

        # calculate SAT rate
        sat_rate = (sat_count / (sat_count + unsat_count)) * 100

        # for errorbar
        # max_elapsed_time = max(elapsed_time_list)
        # mean_elapsed_time = mean(elapsed_time_list)
        # min_elapsed_time = min(elapsed_time_list)
        # mean_elapsed_time_list.append(mean_elapsed_time)
        # upper_err_list.append(max_elapsed_time - mean_elapsed_time)
        # lower_err_list.append(mean_elapsed_time - min_elapsed_time)

        # for boxplot
        if sat_rate > 3:
            elapsed_time_list_list.append(elapsed_time_list)
            sat_rate_list.append(sat_rate)
        else:
            break


    # for errorbar
    # x = np.array(num_flow_hard_list)
    # y = np.array(mean_elapsed_time_list)
    # y_err = np.array([lower_err_list] + [upper_err_list])

    # generate graph
    # gen_time_graph_for_hard_errorbar(x, y, y_err)
    gen_time_graph_for_hard_boxplot(num_flow_hard_list, elapsed_time_list_list)
    gen_rate_graph(num_flow_hard_list, sat_rate_list)


def main():
    # for soft scheduling
    # measure_time_for_soft()

    # for hard scheduling
    measure_time_for_hard()

if __name__ == "__main__":
    main()
