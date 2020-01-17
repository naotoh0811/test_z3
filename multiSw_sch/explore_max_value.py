import numpy as np
import os.path
import sys
import pprint
import itertools
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.sch_with_soft as sch_with_soft
import network.dijkstra.gen_flowData as gen_flowData
sys.path.append('{}/IEEE8021Q_test'.format(home_dir))
import results.calc_value as calc_value

def get_latency_list_from_csv(csv_filename):
    latency_list = []
    with open(csv_filename, 'r') as f:
        line = f.readline()
        while line:
            latency = float(line.strip()) * (10 ** 6)
            latency_list.append(latency)
            line = f.readline()
    
    return latency_list

def get_latency_hist_from_list(latency_list):
    hist, bins = np.histogram(latency_list, bins=30)

    probability = hist / len(latency_list)

    bins_delta = np.diff(bins)[0] / 2
    half_bins = bins + bins_delta

    return probability, half_bins[:-1]

def get_expected_val_from_histgram_and_tuf(probability, half_bins, tuf):
    expected_val = 0
    for each_probability, each_latency in zip(probability, half_bins):
        val = calc_value.calc_value_using_tuf(each_latency, tuf)
        expected_val += val * each_probability

    return expected_val

def get_priority_from_flow_id(flow_id):
    gcl_filename = \
        '{}/workspace/test_z3/multiSw_sch/gcl_cli_send.yml'.format(home_dir)
    gcl_yaml = gen_flowData.read_yaml(gcl_filename)

    for each_gcl in gcl_yaml:
        if flow_id == each_gcl["flow_id"]:
            return each_gcl["priority"]
    
    raise Exception('Can not find flow whose flow_id is {}'.format(flow_id))

def get_hist_list_from_flow_list(flow_list_soft, for_measure=False):
    hist_and_priority_dic_list = []
    flow_prio_list = []
    prio_for_measure = 0
    for each_flow in flow_list_soft:
        # get flow info
        flow_id = each_flow["flow_id"]
        if not for_measure:
            priority = get_priority_from_flow_id(flow_id)
        else:
            priority = prio_for_measure
            prio_for_measure = min(prio_for_measure + 1, 6)

        # check flow_prio_list
        if priority in flow_prio_list:
            flow_prio_list.append(priority)
            continue
        flow_prio_list.append(priority)

        # get latency_list and hist
        csv_filename = '{}/IEEE8021Q_test/results/latency{}.csv'.format(home_dir, flow_id)
        latency_list = get_latency_list_from_csv(csv_filename)
        probability, half_bins = get_latency_hist_from_list(latency_list)

        hist_and_priority_dic_list.append({ \
            "priority": priority, \
            "probability": probability, \
            "half_bins": half_bins \
        })

    return hist_and_priority_dic_list, flow_prio_list

def explore_max_value_from_lists(flow_list_soft, hist_and_priority_dic_list, prio_permutation_list):
    max_sum_expected_value = 0
    for each_permutation in prio_permutation_list:
        sum_expected_val = 0
        for i, each_flow in enumerate(flow_list_soft):
            # get flow info
            tuf = each_flow["tuf"]

            # get priority from permutation list
            # print(i, each_permutation)
            priority = each_permutation[i]

            # get hist
            probability = hist_and_priority_dic_list[priority]["probability"]
            half_bins = hist_and_priority_dic_list[priority]["half_bins"]

            # get expected value
            expected_val = get_expected_val_from_histgram_and_tuf(probability, half_bins, tuf)
            sum_expected_val += expected_val

        # check sum_expected_val
        # print(sum_expected_val)
        if sum_expected_val > max_sum_expected_value:
            max_sum_expected_value = sum_expected_val
            max_prio_permutation_list = each_permutation

    return max_sum_expected_value, max_prio_permutation_list

def main():
    # get flow list
    flow_with_path_soft_filename = \
        '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir)
    _, flow_list_soft, _, _ = sch_with_soft.check_existence_and_get_flow_list( \
        '', flow_with_path_soft_filename)
    
    # get latency_list and hist for prio
    hist_and_priority_dic_list, flow_prio_list = \
        get_hist_list_from_flow_list(flow_list_soft, for_measure=False)

    # sort list by priority
    # list index is equal to priority
    hist_and_priority_dic_list = sorted(hist_and_priority_dic_list, reverse=False, key=lambda x:x["priority"])

    # get permutation list
    prio_permutation_list = list(itertools.permutations(flow_prio_list))

    # explore max value
    max_sum_expected_value, max_prio_permutation_list = \
        explore_max_value_from_lists(flow_list_soft, hist_and_priority_dic_list, prio_permutation_list)

    return max_sum_expected_value, max_prio_permutation_list

if __name__ == "__main__":
    print(main())