import numpy as np
import yaml
import os.path
import sys
import pprint
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

def get_latency_histgram(latency_list):
    hist, bins = np.histogram(latency_list, bins=10)

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


if __name__ == "__main__":
    # get flow list
    flow_with_path_hard_filename = \
        '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir)
    flow_with_path_soft_filename = \
        '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir)
    flow_list_hard, flow_list_soft, onlyHard, onlySoft = sch_with_soft.check_existence_and_get_flow_list( \
        flow_with_path_hard_filename, flow_with_path_soft_filename)
    
    # get latency_list and hist for prio
    hist_and_priority_dic_list = []
    for each_flow in flow_list_soft:
        flow_id = each_flow["flow_id"]
        priority = get_priority_from_flow_id(flow_id)
        csv_filename = '{}/IEEE8021Q_test/results/latency{}.csv'.format(home_dir, flow_id)
        latency_list = get_latency_list_from_csv(csv_filename)
        probability, half_bins = get_latency_histgram(latency_list)

        hist_and_priority_dic_list.append({ \
            "priority": priority, \
            "probability": probability, \
            "half_bins": half_bins \
        })

    # pprint.pprint(hist_and_priority_dic_list)

    # sum_expected_val = 0
    # for each_flow in flow_list_soft:
    #     tuf = each_flow["tuf"]
    #     expected_val = get_expected_val_from_histgram_and_tuf(probability, half_bins, tuf)
    #     sum_expected_val += expected_val
    