import os
import glob
import sys
import subprocess
import pprint
import yaml
import time
import copy
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.sch as sch
import multiSw_sch.gen_window_graph as gen_window_graph
sys.path.append('{}/IEEE8021Q_test'.format(home_dir))
import results.calc_value as calc_value

NOT_DEFINE = 1000
UNSAT = -2
SAT = -1

light_speed = 5 * (10 ** (-3)) # in us/m
link_length = 10
link_bandwidth = 100 # in Mbps

def check_existence_and_get_flow_list(flow_with_path_hard_filename, flow_with_path_soft_filename):
    # get flow_list from yaml
    # i_flow_dic in these lists are not valid. Don't reference it.
    onlyHard = False
    onlySoft = False
    if os.path.exists(flow_with_path_hard_filename):
        flow_list_hard = sch.get_flow_list_from_yaml(flow_with_path_hard_filename)
        num_hard = len(flow_list_hard)
        print('num_hard: {}'.format(num_hard), end=' ')
    else:
        onlySoft = True
    if os.path.exists(flow_with_path_soft_filename):
        flow_list_soft = sch.get_flow_list_from_yaml(flow_with_path_soft_filename)
        num_soft = len(flow_list_soft)
        print('num_soft: {}'.format(num_soft), end=' ')
    else:
        onlyHard = True
    if onlyHard and onlySoft:
        print('ERROR: Maybe flow_with_path is not exist.')
    print('| ', end='')

    return flow_list_hard, flow_list_soft, onlyHard, onlySoft

def repeat_schedule_with_soft(flow_list_hard, flow_list_soft, onlyHard, onlySoft, notPrioritize=False):
    # calculate pseudo slope and rearrange
    if not onlyHard:
        # sorted_flow_list_soft = calc_pseudo_slope(flow_list_soft)
        sorted_flow_list_soft = calc_minLatency_val(flow_list_soft)

    start_time = time.time()

    # schedule only hard
    if not onlySoft:
        sat_or_unsat = sch.main(flow_list_hard)
        sch_time_only_hard = time.time() - start_time
        if sat_or_unsat == UNSAT:
            return UNSAT, [], 0, 0
        elif onlyHard: # onlyHard and SAT
            return SAT, [], sch_time_only_hard, 0
    else: # onlySoft
        sch_time_only_hard = 0
    
    # if don't schedule soft flows
    if notPrioritize:
        return -1, flow_list_soft, sch_time_only_hard, 0
    
    start_time = time.time()

    # schedule with soft
    if not onlyHard:
        sorted_flow_list_low_prio = []
        if onlySoft:
            flow_list_hard_with_soft = []
        else:
            flow_list_hard_with_soft = copy.deepcopy(flow_list_hard)
        for i_repeat in range(len(sorted_flow_list_soft)):
            flow_list_hard_with_soft.append(sorted_flow_list_soft[i_repeat])
            sat_or_unsat = sch.main(flow_list_hard_with_soft)
            # print('flow_hard + flow_soft[0]~[{}] -> '.format(i_repeat), end="")
            # print('sat' if sat_or_unsat == SAT else 'unsat')
            # print("--------------------")

            if sat_or_unsat == UNSAT:
                # if onlySoft and can not schedule even first flow, gcl_cli_send.yml is not updated.
                # so delete old gcl_cli_send_yml
                if onlySoft and i_repeat == 0:
                    gcl_cli_send_filename = '{}/workspace/test_z3/multiSw_sch/gcl_cli_send.yml'.format(home_dir)
                    if os.path.exists(gcl_cli_send_filename):
                        os.remove(gcl_cli_send_filename)
                i_last_flow = i_repeat - 1
                sorted_flow_list_low_prio = sorted_flow_list_soft[i_last_flow + 1:]

                sch_time_with_soft = time.time() - start_time

                return i_last_flow, sorted_flow_list_low_prio, sch_time_only_hard, sch_time_with_soft

        i_last_flow = i_repeat
        sch_time_with_soft = time.time() - start_time

        return i_last_flow, sorted_flow_list_low_prio, sch_time_only_hard, sch_time_with_soft

def calc_pseudo_slope(flow_list_soft):
    for each_flow in flow_list_soft:
        first_tuf = each_flow["tuf"][0]
        first_val = first_tuf[4]

        last_tuf = each_flow["tuf"][-1]
        last_slope = last_tuf[3]
        last_y_intercept = last_tuf[4]
        x_intercept = -(last_y_intercept / last_slope)

        pseudo_slope = first_val / x_intercept
        each_flow["pseudo_slope"] = pseudo_slope
    
    sorted_flow_list_soft = sorted(flow_list_soft, reverse=True, key=lambda x:x["pseudo_slope"])
    # pprint.pprint(sorted_flow_list_soft)

    return sorted_flow_list_soft

def calc_minLatency_val(flow_list_soft):
    for each_flow in flow_list_soft:
        # calculate minLatency latency
        num_hop = len(each_flow["node_list"]) - 1
        size = each_flow["size"]
        minLatency_latency = (size * 8 / link_bandwidth + light_speed * link_length) * num_hop

        # get TUF
        tuf = each_flow["tuf"]

        # calculate minLatency value
        minLatency_val = calc_value.calc_value_using_tuf(minLatency_latency, tuf)

        # add minLatency value to dict
        each_flow["minLatency_val"] = minLatency_val

    sorted_flow_list_soft = sorted(flow_list_soft, reverse=True, key=lambda x:x["minLatency_val"])
    pprint.pprint(sorted_flow_list_soft)

    return sorted_flow_list_soft

def output_yaml_cli_send_low_prio(sorted_flow_list_low_prio, output_filename, notPrioritize=False):
    prio = 6
    yaml_output = []
    for each_flow in sorted_flow_list_low_prio:
        yaml_each_cli = { \
            "flow_id": each_flow["flow_id"], \
            "name": each_flow["node_list"][0], \
            "pass_node_list": each_flow["node_list"][1:], \
            "cycle": each_flow["cycle"], \
            "size": each_flow["size"], \
            "priority": prio, \
            "send_time": 10}

        yaml_output.append(yaml_each_cli)

        if not notPrioritize:
            prio = max(prio - 1, 0)

    with open(output_filename, "a") as f:
        f.write(yaml.dump(yaml_output))
    # pprint.pprint(sorted_flow_list_low_prio)

def output_params_to_csv(bandwidth_hard, bandwidth_soft, num_hard, num_soft, i_last_flow, sch_time_only_hard, sch_time_with_soft, notPrioritize):
    output_filename = \
        '{}/IEEE8021Q_test/results/params_and_results{}.csv'.format(home_dir, '_np' if notPrioritize else '')
    if not os.path.isfile(output_filename):
        with open(output_filename, 'w') as f:
            output_csv = ''
            output_csv += 'bandwidth_hard,'
            output_csv += 'bandwidth_soft,'
            output_csv += 'num_hard,'
            output_csv += 'num_soft,'
            output_csv += 'i_last_flow,'
            output_csv += 'sch_time_only_hard,'
            output_csv += 'sch_time_only_soft,'
            output_csv += 'mean_val_rate,'
            output_csv += 'burst_rate\n'
            f.write(output_csv)
    with open(output_filename, 'a') as f:
        f.write('{},{},{},{},{},{},{},'.format( \
            bandwidth_hard, bandwidth_soft, num_hard, num_soft, i_last_flow, sch_time_only_hard, sch_time_with_soft \
        ))
        if i_last_flow == UNSAT:
            f.write('-,-\n')

def get_bandwidth_from_flow_list(flow_list_hard):
    cum_bandwidth = 0
    for each_flow in flow_list_hard:
        cycle = each_flow["cycle"]
        size = each_flow["size"]
        bandwidth = (size * 8) / cycle # in Mbps
        cum_bandwidth += bandwidth
    
    return cum_bandwidth


def main(notPrioritize):
    flow_with_path_hard_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir)
    flow_with_path_soft_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir)

    # get flow list
    flow_list_hard, flow_list_soft, onlyHard, onlySoft = check_existence_and_get_flow_list( \
        flow_with_path_hard_filename, flow_with_path_soft_filename)

    # schedule with hard and soft
    i_last_flow, sorted_flow_list_low_prio, sch_time_only_hard, sch_time_with_soft = \
        repeat_schedule_with_soft(flow_list_hard, flow_list_soft, onlyHard, onlySoft, notPrioritize)

    if i_last_flow == UNSAT:
        print('can not schedule')
    elif i_last_flow == -1:
        print('can schedule only hard')
    else:
        print('can schedule with flow_soft[0]~[{}]'.format(i_last_flow))

    if len(sorted_flow_list_low_prio) != 0:
        output_filename = '{}/workspace/test_z3/multiSw_sch/gcl_cli_send.yml'.format(home_dir)
        # output_yaml_cli_send_low_prio(sorted_flow_list_low_prio, output_filename)
        output_yaml_cli_send_low_prio(sorted_flow_list_low_prio, output_filename, notPrioritize)

    # remove old pdf files
    for pdf_file in glob.glob(home_dir + '/workspace/test_z3/multiSw_sch/window_sw*.pdf'):
        if os.path.isfile(pdf_file):
            os.remove(pdf_file)
    # generate window graph
    gen_window_graph.main()

    # get bandwidth
    bandwidth_hard = get_bandwidth_from_flow_list(flow_list_hard)
    bandwidth_soft = get_bandwidth_from_flow_list(flow_list_soft)
    # get number of flow
    num_hard = len(flow_list_hard)
    num_soft = len(flow_list_soft)
    # output flow and scheduling information to csv
    output_params_to_csv(bandwidth_hard, bandwidth_soft, num_hard, num_soft, i_last_flow, sch_time_only_hard, sch_time_with_soft, notPrioritize)

    return i_last_flow, sch_time_only_hard, sch_time_with_soft


if __name__ == "__main__":
    notPrioritize = True if len(sys.argv)>1 and sys.argv[1] == 'True' else False
    i_last_flow, sch_time_only_hard, sch_time_with_soft = main(notPrioritize)
    if i_last_flow == UNSAT:
        raise Exception('Can not schedule even if only HARD.')