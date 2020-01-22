import os.path
import sys
import time
import itertools
from math import factorial
from statistics import mean
import numpy as np
import yaml
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


def get_result_list_for_soft(max_num_flow_soft):
    num_flow_soft_list = range(2, max_num_flow_soft + 1)
    elapsed_time_list_list = []
    for num_flow in num_flow_soft_list:
        elapsed_time_list = []
        for i in range(1):
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
            _, max_prio_permutation_list = \
                explore_max_value.explore_max_value_from_lists(flow_list, hist_and_priority_dic_list, prio_permutation_list)
            elapsed_time = time.time() - start_time

            print(num_flow, elapsed_time)
            elapsed_time_list.append(elapsed_time)

        # output to yaml
        output_list = [{
            "num_flow_soft": num_flow,
            "elapsed_time_list": elapsed_time_list
        }]
        output_filename = '{}/workspace/test_z3/multiSw_sch/data/time_soft.yml'.format(home_dir)
        # output_to_yaml(output_list, output_filename)

        # append list_list
        elapsed_time_list_list.append(elapsed_time_list)

    return num_flow_soft_list, elapsed_time_list_list

def gen_dammy_flow_list(num_flow):
    dammy_flow_list = []
    for flow_id in range(num_flow):
        flow_dic = {
            # "flow_id": random.randint(0, 6),
            "flow_id": flow_id,
            "tuf": [[0, 19.596, "linear", 0, 100], [19.596, 55.596, "linear", -2.778, 154.4]]
        }
        dammy_flow_list.append(flow_dic)

    return dammy_flow_list

def gen_time_graph_for_soft_plot(result_list, max_num_flow_soft):
    # generate num_flow list
    num_flow_soft_list = range(2, max_num_flow_soft + 1)

    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    fig, ax = plt.subplots()

    # plot
    p = ax.plot(num_flow_soft_list, result_list, marker=".", c='b')

    # set scale
    ax.set_yscale('log')

    # set label
    font_size_label = 18
    ax.set_xlabel('Number of soft real-time flows', fontsize=font_size_label)
    ax.set_ylabel('Calculation time [s]', fontsize=font_size_label)

    # set ticks
    ax.set_xticks(range(2, 11))

    # set grid
    ax.grid()

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('{}/workspace/test_z3/multiSw_sch/pdf/num_soft_flow_vs_time.pdf'.format(home_dir))

def gen_time_graph_for_soft_errorbar(y, y_err, order_list, max_num_flow_soft):
    # generate num_flow list
    num_flow_soft_list = range(2, max_num_flow_soft + 1)
    x = np.array(num_flow_soft_list)

    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14

    fig, ax = plt.subplots()

    # plot result
    plt.rcParams["errorbar.capsize"] = 5
    ax.errorbar(x, y, yerr=y_err, fmt='b.-', label='Measured time')

    # plot order
    ax.plot(x, order_list, color='r', marker='.', label='Estimated time')

    # set scale
    ax.set_yscale('log')

    # set label
    font_size_label = 18
    ax.set_xlabel('Number of soft real-time flows', fontsize=font_size_label)
    ax.set_ylabel('Calculation time [s]', fontsize=font_size_label)

    # set ticks
    ax.set_xticks(range(2, 11))

    # set grid
    ax.grid()

    # set legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    # shape layout
    plt.tight_layout()
    # make pdf
    make_pdf('{}/workspace/test_z3/multiSw_sch/pdf/num_soft_flow_vs_time.pdf'.format(home_dir))

def gen_time_graph_for_hard_errorbar(y, y_err, max_num_flow_hard):
    # generate num_flow list
    num_flow_hard_list = range(1, max_num_flow_hard + 1)
    x = np.array(num_flow_hard_list)

    # set font
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 11

    fig, ax = plt.subplots()

    # plot
    ax.errorbar(x, y, yerr=y_err, fmt='b.-')

    # set label
    font_size_label = 18
    ax.set_xlabel('Number of hard real-time flows', fontsize=font_size_label)
    ax.set_ylabel('Calculation time [s]', fontsize=font_size_label)

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
    plt.rcParams["font.size"] = 15

    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(111)

    # plot
    ax.boxplot(elapsed_time_list_list, labels=num_flow_hard_list, patch_artist=True, \
        boxprops={'facecolor': 'lightblue'})

    # set label
    font_size_label = 18
    ax.set_xlabel('Number of hard real-time flows', fontsize=font_size_label)
    ax.set_ylabel('Calculation time [s]', fontsize=font_size_label)

    # set ticks
    # max_num_flow_hard = num_flow_hard_list[-1]
    # ax.set_xticks(range(1, max_num_flow_hard + 1))

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
    ax.set_ylim(0, 100)

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

def output_to_yaml(output_list, output_filename):
    with open(output_filename, "a") as f:
        f.write(yaml.dump(output_list))

def get_result_list_for_hard(max_num_flow_hard):
    num_flow_hard_list = range(30, max_num_flow_hard + 1)
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

        # for boxplot
        if sat_rate > 3:
            elapsed_time_list_list.append(elapsed_time_list)
            sat_rate_list.append(sat_rate)

            output_list = [{
                "num_flow_hard": num_flow_hard,
                "elapsed_time_list": elapsed_time_list,
                "sat_rate": sat_rate
            }]
            output_filename = '{}/workspace/test_z3/multiSw_sch/data/time_and_rate_hard.yml'.format(home_dir)
            output_to_yaml(output_list, output_filename)
        else:
            break

    return num_flow_hard_list, elapsed_time_list_list, sat_rate_list

def get_result_list_from_yaml_hard():
    yaml_filename = '{}/workspace/test_z3/multiSw_sch/data/time_and_rate_hard.yml'.format(home_dir)
    with open(yaml_filename, "r+") as f:
        result_list = yaml.load(f, yaml.SafeLoader)

    num_flow_hard_list = []
    elapsed_time_list_list = []
    sat_rate_list = []
    for each_result in result_list:
        num_flow_hard_list.append(each_result["num_flow_hard"])
        elapsed_time_list_list.append(each_result["elapsed_time_list"])
        sat_rate_list.append(each_result["sat_rate"])

    return num_flow_hard_list, elapsed_time_list_list, sat_rate_list

def get_result_list_from_yaml_soft():
    yaml_filename = '{}/workspace/test_z3/multiSw_sch/data/time_soft.yml'.format(home_dir)
    with open(yaml_filename, "r+") as f:
        result_list = yaml.load(f, yaml.SafeLoader)

    elapsed_time_list_list = []
    for each_result in result_list:
        elapsed_time_list_list.append(each_result["elapsed_time_list"])

    return elapsed_time_list_list

def change_list_for_errorbar(result_list):
    mean_list = []
    lower_err_list = []
    upper_err_list = []
    for each_list in result_list:
        mean_val = mean(each_list)
        lower_err = mean_val - min(each_list)
        upper_err = max(each_list) - mean_val

        mean_list.append(mean_val)
        lower_err_list.append(lower_err)
        upper_err_list.append(upper_err)

    # list -> array
    y = np.array(mean_list)
    y_err = np.array([lower_err_list] + [upper_err_list])

    return y, y_err

def get_order_val_list(max_num_flow_soft):
    return [0.0000004 * i * factorial(i) for i in range(2, max_num_flow_soft + 1)]

def measure_time_for_soft():
    max_num_flow_soft = 10

    # get result list
    # num_flow_soft_list, elapsed_time_list_list = get_result_list_for_soft(max_num_flow_soft)
    elapsed_time_list_list = get_result_list_from_yaml_soft()

    # generate graph
    y, y_err = change_list_for_errorbar(elapsed_time_list_list)
    order_list = get_order_val_list(max_num_flow_soft)
    gen_time_graph_for_soft_errorbar(y, y_err, order_list, max_num_flow_soft)

def measure_time_for_hard():
    # get result list
    max_num_flow_hard = 30
    # num_flow_hard_list, elapsed_time_list_list, sat_rate_list = \
    #     get_result_list_for_hard(max_num_flow_hard)
    num_flow_hard_list, elapsed_time_list_list, sat_rate_list = get_result_list_from_yaml_hard()

    # generate graph
    y, y_err = change_list_for_errorbar(elapsed_time_list_list)
    # gen_time_graph_for_hard_boxplot(num_flow_hard_list, elapsed_time_list_list)
    gen_time_graph_for_hard_errorbar(y, y_err, max_num_flow_hard)
    gen_rate_graph(num_flow_hard_list, sat_rate_list)


def main():
    # for soft scheduling
    measure_time_for_soft()

    # for hard scheduling
    # measure_time_for_hard()

if __name__ == "__main__":
    main()
