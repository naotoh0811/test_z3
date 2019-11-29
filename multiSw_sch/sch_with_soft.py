import os.path
import sys
import subprocess
import pprint
import yaml
import time
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.sch as sch

NOT_DEFINE = 1000
UNSAT = -2
SAT = -1

def repeat_schedule_with_soft(flow_with_path_hard_filename, flow_with_path_soft_filename):
    # get flow_lsit from yaml
    # i_flow_dic in these lists are not valid. Don't reference it.
    onlyHard = False
    onlySoft = False
    if os.path.exists(flow_with_path_hard_filename):
        flow_list_hard = sch.get_flow_list_from_yaml(flow_with_path_hard_filename)
    else:
        onlySoft = True
    if os.path.exists(flow_with_path_soft_filename):
        flow_list_soft = sch.get_flow_list_from_yaml(flow_with_path_soft_filename)
    else:
        onlyHard = True
    if onlyHard and onlySoft:
        print('ERROR: Maybe flow_with_path is not exist.')

    # calculate pseudo slope and rearrange
    if not onlyHard:
        sorted_flow_list_soft = calc_pseudo_slope(flow_list_soft)

    # schedule only hard
    if not onlySoft:
        sat_or_unsat = sch.main(flow_list_hard)
        if sat_or_unsat == UNSAT:
            return UNSAT, []
        elif onlyHard: # onlyHard and SAT
            return SAT, []
    
    # schedule with soft
    if not onlyHard:
        sorted_flow_list_low_prio = []
        if onlySoft:
            flow_list_hard_with_soft = []
        else:
            flow_list_hard_with_soft = flow_list_hard
        for i_repeat in range(len(sorted_flow_list_soft)):
            flow_list_hard_with_soft.append(sorted_flow_list_soft[i_repeat])
            sat_or_unsat = sch.main(flow_list_hard_with_soft)
            # print('flow_hard + flow_soft[0]~[{}] -> '.format(i_repeat), end="")
            # print('sat' if sat_or_unsat == SAT else 'unsat')

            if sat_or_unsat == UNSAT:
                if onlySoft and i_repeat == 0:
                    return UNSAT, []
                i_last_flow = i_repeat - 1
                sorted_flow_list_low_prio = sorted_flow_list_soft[i_last_flow + 1:]
                return i_last_flow, sorted_flow_list_low_prio

        i_last_flow = i_repeat
        return i_last_flow, sorted_flow_list_low_prio

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

def output_yaml_cli_send_low_prio(sorted_flow_list_low_prio, output_filename):
    prio = 6
    yaml_output = []
    for each_flow in sorted_flow_list_low_prio:
        yaml_each_cli = { \
            "flow_id": each_flow["flow_id"], \
            "name": each_flow["node_list"][0], \
            "pass_node_list": each_flow["node_list"][1:], \
            "cycle": each_flow["cycle"], \
            "priority": prio, \
            "send_time": 10}

        yaml_output.append(yaml_each_cli)

        prio = max(prio - 1, 0)

    with open(output_filename, "a") as f:
        f.write(yaml.dump(yaml_output))
    # pprint.pprint(sorted_flow_list_low_prio)

def main():
    home_dir = os.path.expanduser('~')
    flow_with_path_hard_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir)
    flow_with_path_soft_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir)

    start_time = time.time()

    # schedule with hard, soft
    i_last_flow, sorted_flow_list_low_prio = \
        repeat_schedule_with_soft(flow_with_path_hard_filename, flow_with_path_soft_filename)

    elapsed_time = time.time() - start_time
    # print('elapsed_time: {}'.format(elapsed_time))

    # if i_last_flow == UNSAT:
    #     print('can not schedule')
    # elif i_last_flow == -1:
    #     print('can schedule only hard')
    # else:
    #     print('can schedule with flow_soft[0]~[{}]'.format(i_last_flow))

    if len(sorted_flow_list_low_prio) != 0:
        output_yaml_cli_send_low_prio(sorted_flow_list_low_prio, \
            '{}/workspace/test_z3/multiSw_sch/gcl_cli_send.yml'.format(home_dir))

    return i_last_flow, elapsed_time


if __name__ == "__main__":
    main()