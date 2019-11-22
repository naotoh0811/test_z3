import os.path
import sys
import subprocess
import pprint
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.sch as sch

NOT_DEFINE = 1000
UNSAT = -2
SAT = -1

def repeat_schedule_with_soft(flow_with_path_hard_filename, flow_with_path_soft_filename):
    flow_list_hard = sch.get_flow_list_from_yaml(flow_with_path_hard_filename)
    flow_list_soft = sch.get_flow_list_from_yaml(flow_with_path_soft_filename)

    sorted_flow_list_soft = calc_pseudo_slope(flow_list_soft)

    # schedule only hard
    sat_or_unsat = sch.main(flow_list_hard)
    if sat_or_unsat == UNSAT:
        return UNSAT
    
    # schedule with soft
    flow_list_hard_with_soft = flow_list_hard
    for i_repeat in range(len(sorted_flow_list_soft)):
        flow_list_hard_with_soft.append(sorted_flow_list_soft[i_repeat])
        sat_or_unsat = sch.main(flow_list_hard_with_soft)
        print('flow_hard + flow_soft[0]~[{}] -> '.format(i_repeat), end="")
        print('sat' if sat_or_unsat == SAT else 'unsat')

        if sat_or_unsat == UNSAT:
            return i_repeat - 1

    return i_repeat

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


def main():
    home_dir = os.path.expanduser('~')
    flow_with_path_hard_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir)
    flow_with_path_soft_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir)

    i_last_chosen_flow_soft = repeat_schedule_with_soft(flow_with_path_hard_filename, flow_with_path_soft_filename)
    if i_last_chosen_flow_soft == UNSAT:
        print('cant schedule')
    elif i_last_chosen_flow_soft == -1:
        print('can schedule only hard')
    else:
        print('can schedule with flow_soft[0]~[{}]'.format(i_last_chosen_flow_soft))


if __name__ == "__main__":
    main()