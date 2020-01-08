import os
import glob
import sys
import pprint
import yaml
import time
import random
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.sch as sch
import multiSw_sch.sch_with_soft as sch_with_soft
import multiSw_sch.gen_window_graph as gen_window_graph
import multiSw_sch.explore_max_value as explore_max_value
import network.flow.gen_flow_using_network_csv as gen_flow_using_network_csv
sys.path.append('{}/IEEE8021Q_test'.format(home_dir))
import results.calc_value as calc_value

NOT_DEFINE = 1000
UNSAT = -2
SAT = -1

# kind_prioritize
SORT = 0
RANDOM = 1
NONE = 2
HIST = 3

light_speed = 5 * (10 ** (-3)) # in us/m
link_length = 10
link_bandwidth = 1000 # in Mbps

def output_yaml_cli_send_low_prio( \
        flow_list_soft, max_prio_permutation_list, output_filename, kind_prioritize=SORT \
    ):
    if max_prio_permutation_list == [] and kind_prioritize == SORT:
        raise Exception('max_prio_permutation is empty.')

    prio = 0
    yaml_output = []
    for i, each_flow in enumerate(flow_list_soft):
        # determine prio
        if kind_prioritize == SORT:
            prio = max_prio_permutation_list[i]
        elif kind_prioritize == RANDOM:
            prio = random.randint(0, 6)

        # determine cycle
        cycle = each_flow["cycle"]
        send_time = (10 + 10 * i) % cycle

        yaml_each_cli = { \
            "flow_id": each_flow["flow_id"], \
            "name": each_flow["node_list"][0], \
            "pass_node_list": each_flow["node_list"][1:], \
            "cycle": cycle, \
            "size": each_flow["size"], \
            "priority": prio, \
            "send_time": send_time}

        yaml_output.append(yaml_each_cli)

        # prio for hist
        if kind_prioritize == HIST:
            prio = min(prio + 1, 6)

    with open(output_filename, "a") as f:
        f.write(yaml.dump(yaml_output))


def main(kind_prioritize):
    flow_with_path_hard_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir)
    flow_with_path_soft_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir)

    # get flow list
    flow_list_hard, flow_list_soft, onlyHard, onlySoft = sch_with_soft.check_existence_and_get_flow_list( \
        flow_with_path_hard_filename, flow_with_path_soft_filename)

    # schedule soft
    start_time = time.time()
    max_prio_permutation_list = []
    if kind_prioritize == SORT:
        _, max_prio_permutation_list = explore_max_value.main()
    sch_time_only_soft = time.time() - start_time

    # schedule hard
    start_time = time.time()
    if not onlySoft:
        sat_or_unsat = sch.main(flow_list_hard)
        if sat_or_unsat == UNSAT:
            raise Exception('UNSAT')
    sch_time_only_hard = time.time() - start_time

    # if onlySoft, gcl_cli_send.yml is not updated.
    # so delete old gcl_cli_send.yml
    if onlySoft:
        gcl_cli_send_filename = '{}/workspace/test_z3/multiSw_sch/gcl_cli_send.yml'.format(home_dir)
        if os.path.exists(gcl_cli_send_filename):
            os.remove(gcl_cli_send_filename)

    # output gcl for soft
    if len(flow_list_soft) != 0:
        output_filename = '{}/workspace/test_z3/multiSw_sch/gcl_cli_send.yml'.format(home_dir)
        output_yaml_cli_send_low_prio( \
            flow_list_soft, max_prio_permutation_list, output_filename, kind_prioritize)

    if kind_prioritize != HIST:
        # remove old pdf files
        for pdf_file in glob.glob(home_dir + '/workspace/test_z3/multiSw_sch/pdf/window_sw*.pdf'):
            if os.path.isfile(pdf_file):
                os.remove(pdf_file)
        # generate window graph
        gen_window_graph.main()

        # get bandwidth
        bandwidth_hard = sch_with_soft.get_bandwidth_from_flow_list(flow_list_hard)
        bandwidth_soft = sch_with_soft.get_bandwidth_from_flow_list(flow_list_soft)
        # get number of flow
        num_hard = len(flow_list_hard)
        num_soft = len(flow_list_soft)
        # output flow and scheduling information to csv
        sch_with_soft.output_params_to_csv( \
            bandwidth_hard, bandwidth_soft, num_hard, num_soft, -1, sch_time_only_hard, sch_time_only_soft, kind_prioritize)


if __name__ == "__main__":
    kind_prioritize = SORT
    if len(sys.argv) > 1:
        if sys.argv[1] == 'RANDOM':
            kind_prioritize = RANDOM
        elif sys.argv[1] == 'NONE':
            kind_prioritize = NONE
        elif sys.argv[1] == 'HIST':
            kind_prioritize = HIST

    main(kind_prioritize)