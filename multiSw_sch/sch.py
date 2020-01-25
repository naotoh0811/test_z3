from z3 import *
import pandas as pd
import yaml
import math
import os.path
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import multiSw_sch.lcm as lcm

NOT_DEFINE = 1000
UNSAT = -2
SAT = -1

light_speed = 5 * (10 ** (-3)) # in us/m
link_length = 10
link_bandwidth = 1000 # in Mbps

def get_flow_list_from_csv(filename): # not used
    df = pd.read_csv(filename)
    flow_list = []
    i_flow_dic_cum = {}
    for row in df.itertuples():
        flow_id = row.flow_id
        cycle = int(row.cycle)

        node_list = row.node_list.split()
        node_list = [int(i) for i in node_list]

        i_flow_dic = {}
        node_list_only_sw = node_list[1:-1]
        for node in node_list_only_sw:
            if node in i_flow_dic_cum:
                i_flow_dic_cum[node] += 1
            else:
                i_flow_dic_cum[node] = 0
            i_flow_dic[node] = i_flow_dic_cum[node]

        size = row.size
        ocu_time = math.ceil(size * 8 / link_bandwidth + light_speed * link_length)
        deadline = row.deadline

        flow_list.append({ \
            "flow_id": flow_id, \
            "cycle": cycle, \
            "node_list": node_list, \
            "i_flow_dic": i_flow_dic, \
            "ocu_time": ocu_time, \
            "deadline": deadline})

    return flow_list

def get_flow_list_from_yaml(filename):
    f = open(filename, "r+")
    flow_list_from_yaml = yaml.load(f, yaml.SafeLoader)

    i_flow_dic_cum = {}
    size_list = []
    for each_flow in flow_list_from_yaml:
        node_list = each_flow["node_list"]

        i_flow_dic = {}
        node_list_only_sw = node_list[1:-1]
        for node in node_list_only_sw:
            if node in i_flow_dic_cum:
                i_flow_dic_cum[node] += 1
            else:
                i_flow_dic_cum[node] = 0
            i_flow_dic[node] = i_flow_dic_cum[node]

        size = each_flow["size"]
        size_list.append(size)
        ocu_time = math.ceil(size * 8 / link_bandwidth + light_speed * link_length)

        each_flow["i_flow_dic"] = i_flow_dic # {0: 0, 1: 2, 2: 0}
        each_flow["ocu_time"] = ocu_time
    
    return flow_list_from_yaml

def get_flow_list_from_external_flow_list(external_flow_list):
    i_flow_dic_cum = {}
    for each_flow in external_flow_list:
        node_list = each_flow["node_list"]

        i_flow_dic = {}
        node_list_only_sw = node_list[1:-1]
        for node in node_list_only_sw:
            if node in i_flow_dic_cum:
                i_flow_dic_cum[node] += 1
            else:
                i_flow_dic_cum[node] = 0
            i_flow_dic[node] = i_flow_dic_cum[node]

        size = each_flow["size"]
        ocu_time = math.ceil(size * 8 / link_bandwidth + light_speed * link_length)

        each_flow["i_flow_dic"] = i_flow_dic
        each_flow["ocu_time"] = ocu_time

    return external_flow_list

def gen_cycleInSw_dic(flow_list):
    num_flow = len(flow_list)
    cycleInSw_dic = {}
    for each_flow in flow_list:
        node_list = each_flow["node_list"]
        node_list_only_sw = node_list[1:-1]
        for node in node_list_only_sw:
            if not node in cycleInSw_dic:
                cycleInSw_dic[node] = []
            cycleInSw_dic[node].append(each_flow["cycle"])

    return cycleInSw_dic

def gen_superCycle_dic(cycleInSw_dic):
    superCycle_dic = {}
    for (node, cycles) in zip(cycleInSw_dic.keys(), cycleInSw_dic.values()):
        superCycle_dic[node] = lcm.lcm_list(cycles)

    return superCycle_dic

def gen_numWin_dic(cycleInSw_dic, superCycle_dic):
    numWin_dic = {}
    for (node, cycles) in zip(cycleInSw_dic.keys(), cycleInSw_dic.values()):
        superCycle = superCycle_dic[node]
        numWin_dic[node] = [superCycle//cycle for cycle in cycles]
    
    return numWin_dic

def gen_numFlow_in_sw_dic(cycleInSw_dic):
    numFlow_in_sw_dic = {}
    for (node, cycles) in zip(cycleInSw_dic.keys(), cycleInSw_dic.values()):
        numFlow_in_sw_dic[node] = len(cycles)

    return numFlow_in_sw_dic

def gen_nextNode_in_sw_dic(flow_list, numFlow_in_sw_dic):
    nextNode_in_sw_dic = {}
    # init
    for (node, numFlow) in zip(numFlow_in_sw_dic.keys(), numFlow_in_sw_dic.values()):
        nextNode_in_sw_dic[node] = ["-"] * numFlow

    for each_flow in flow_list:
        node_list = each_flow["node_list"]
        node_list = node_list[1:]
        i_flow_dic = each_flow["i_flow_dic"]
        for i_node_list in range(len(node_list)-1):
            node = node_list[i_node_list]
            nextNode = node_list[i_node_list+1]
            i_flow = i_flow_dic[node]
            nextNode_in_sw_dic[node][i_flow] = nextNode

    return nextNode_in_sw_dic

def gen_sw_list(cycleInSw_dic):
    sw_list = []
    for key in cycleInSw_dic.keys():
        sw_list.append(key)

    return sw_list

def get_flow_id_from_i_sw_and_i_flow(flow_list, i_sw, i_flow):
    for each_flow in flow_list:
        i_flow_dic = each_flow["i_flow_dic"]
        if i_sw in i_flow_dic:
            if i_flow_dic[i_sw] == i_flow:
                return each_flow["flow_id"]

    raise Exception('Can not find flow.')

def define_variables_sw(flow_infos):
    ## define open_time, close_time for sw
    open_time = {}
    close_time = {}
    for i_node in flow_infos.sw_list:
        open_time[i_node] = []
        close_time[i_node] = []
        for i_flow in range(flow_infos.numFlow_in_sw_dic[i_node]):
            val_name_open = "open_time[" + str(i_node) + "][" + str(i_flow) + "]"
            val_name_close = "close_time[" + str(i_node) + "][" + str(i_flow) + "]"
            open_time[i_node].append(IntVector(val_name_open, flow_infos.numWin_dic[i_node][i_flow]))
            close_time[i_node].append(IntVector(val_name_close, flow_infos.numWin_dic[i_node][i_flow]))

    return open_time, close_time

def define_variables_cli(flow_list):
    ## define send_time, recv_time for cli
    send_time = {}
    recv_time = {}
    for each_flow in flow_list:
        node_list = each_flow["node_list"]
        src_node = node_list[0]
        dst_node = node_list[-1]
        val_name_send = "send_time[" + str(src_node) +"]"
        val_name_recv = "recv_time[" + str(dst_node) +"]"
        send_time[src_node] = Int(val_name_send)
        recv_time[dst_node] = Int(val_name_recv)

    return send_time, recv_time

def get_deadline(each_flow):
    if "deadline" in each_flow: # hard flow
        return each_flow["deadline"]
    else: # soft flow
        deemed_rate = 1
        tuf = each_flow["tuf"]

        first_val = tuf[0][4]
        deemed_val = first_val * deemed_rate
        deemed_deadline = (deemed_val - tuf[1][4]) / tuf[1][3]

        return deemed_deadline
        # return 0

def add_constraint(flow_list, flow_infos, times_for_gcl, s):
    open_time = times_for_gcl.open_time
    close_time = times_for_gcl.close_time
    send_time = times_for_gcl.send_time
    recv_time = times_for_gcl.recv_time

    for each_flow in flow_list:
        node_list = each_flow["node_list"]
        src_node = node_list[0]
        dst_node = node_list[-1]
        node_list_only_sw = node_list[1:-1]
        cycle = each_flow["cycle"]
        i_flow_dic = each_flow["i_flow_dic"]
        ocu_time = each_flow["ocu_time"]
        link_delay = ocu_time
        deadline = get_deadline(each_flow)
        prev_i_node = NOT_DEFINE
        prev_i_flow = NOT_DEFINE

        # 0 > time
        s.add(send_time[src_node] >= 0)
        s.add(send_time[src_node] <= cycle) # 無くても条件は変わらないが、計算量削減のため上限を設ける
        # deadline
        s.add(recv_time[dst_node] - send_time[src_node] <= deadline - 1)

        for i_node in node_list_only_sw:
            i_flow = i_flow_dic[i_node]
            superCycle = flow_infos.superCycle_dic[i_node]
            i_last_win = flow_infos.numWin_dic[i_node][i_flow] - 1

            for i_win in range(flow_infos.numWin_dic[i_node][i_flow]):
                # fisrt window > 0
                if i_win == 0:
                    s.add(open_time[i_node][i_flow][i_win] >= 0)
                
                # cycle time
                if i_win != i_last_win: # not last win
                    s.add(open_time[i_node][i_flow][i_win+1] - open_time[i_node][i_flow][i_win] == cycle)

                # window does not stride over cycle end point
                # exclusivenessの制約付与の際にこれがないと不具合
                # 正直、適切でない
                s.add(open_time[i_node][i_flow][i_win] % superCycle < close_time[i_node][i_flow][i_win] % superCycle)

                # occupancy time
                s.add(close_time[i_node][i_flow][i_win] - open_time[i_node][i_flow][i_win] == ocu_time)

            if i_node == node_list_only_sw[0]: # first sw
                # from src_node
                # 本来はi_last_winでなく0であるべきだが、なぜか0だとunsatになりがち。
                # おそらくi_last_winでも同じ解を得られる。
                # s.add(open_time[i_node][i_flow][i_last_win] - send_time[src_node] >= link_delay)
                s.add(open_time[i_node][i_flow][0] - send_time[src_node] >= link_delay)
            else: # not first sw
                # next node
                # s.add(open_time[i_node][i_flow][0] - close_time[prev_i_node][prev_i_flow][0] >= link_delay)
                s.add(open_time[i_node][i_flow][0] - open_time[prev_i_node][prev_i_flow][0] >= link_delay)

            if i_node == node_list_only_sw[-1]: # last sw
                # to dst_node
                # 最悪の場合 (closeの瞬間に転送)を想定
                # s.add(recv_time[dst_node] - close_time[i_node][i_flow][i_last_win] >= link_delay)
                # と思っていたが、やっぱりopenの瞬間に転送を想定 既にキューにパケットがある場合を考慮しない
                s.add(recv_time[dst_node] - open_time[i_node][i_flow][0] >= link_delay)

                # これがないと計算時間が無限になる
                # 精々10サイクル分くらいで十分か
                # s.add(close_time[i_node][i_flow][i_last_win] < superCycle*30)
                s.add(recv_time[dst_node] < superCycle*3)

            prev_i_node = i_node
            prev_i_flow = i_flow

    # exclusiveness
    for i_sw in flow_infos.sw_list: # 0,1,2
        superCycle = flow_infos.superCycle_dic[i_sw]
        for i_flow in range(flow_infos.numFlow_in_sw_dic[i_sw]): # i_sw=0なら0,1,2
            nextNode = flow_infos.nextNode_in_sw_dic[i_sw][i_flow]
            for i_win in range(flow_infos.numWin_dic[i_sw][i_flow]): #[0][0]なら0,1,2
                # each win to another win
                for i2_flow in range(flow_infos.numFlow_in_sw_dic[i_sw]):
                    nextNode2 = flow_infos.nextNode_in_sw_dic[i_sw][i2_flow]
                    # apply exclusiveness only when the next nodes of i,i2 are equal
                    if i_flow >= i2_flow or nextNode != nextNode2:
                        continue
                    for i2_win in range(flow_infos.numWin_dic[i_sw][i2_flow]):
                        s.add(Or( \
                            close_time[i_sw][i_flow][i_win] % superCycle <= open_time[i_sw][i2_flow][i2_win] % superCycle, \
                            open_time[i_sw][i_flow][i_win] % superCycle >= close_time[i_sw][i2_flow][i2_win] % superCycle \
                        ))

def check_solver(s):
    r = s.check()
    if r == sat:
        return s.model()
    else:
        # print(r)
        return UNSAT

def print_result_each_sw(flow_infos, times_for_gcl, m):
    open_time = times_for_gcl.open_time
    close_time = times_for_gcl.close_time

    for i_sw in flow_infos.sw_list:
        superCycle = flow_infos.superCycle_dic[i_sw]
        print("sw" + str(i_sw) + " cycle = " + str(superCycle))
        for i_flow in range(flow_infos.numFlow_in_sw_dic[i_sw]):
            nextNode = flow_infos.nextNode_in_sw_dic[i_sw][i_flow]
            print("nextNode: " + str(nextNode))
            for i_win in range(flow_infos.numWin_dic[i_sw][i_flow]):
                real_open_time = m[open_time[i_sw][i_flow][i_win]].as_long() % superCycle
                real_close_time = m[close_time[i_sw][i_flow][i_win]].as_long() % superCycle
                print(real_open_time, real_close_time, end="|")
            print("")
        print("")

def print_result_each_flow(flow_list, flow_infos, times_for_gcl, m):
    open_time = times_for_gcl.open_time
    close_time = times_for_gcl.close_time
    send_time = times_for_gcl.send_time
    recv_time = times_for_gcl.recv_time

    for each_flow in flow_list:
        flow_id = each_flow["flow_id"]
        node_list = each_flow["node_list"]
        src_node = node_list[0]
        dst_node = node_list[-1]
        node_list_only_sw = node_list[1:-1]
        cycle = each_flow["cycle"]
        deadline = get_deadline(each_flow)
        i_flow_dic = each_flow["i_flow_dic"]
        ocu_time = each_flow["ocu_time"]
        
        print("flow_id: {}".format(flow_id))
        print("cycle: {}, node_list: {}, deadline: {}".format(cycle, node_list, deadline))
        # print("send_time: " + str(m[send_time[src_node]].as_long() % cycle))
        print("send_time: " + str(m[send_time[src_node]].as_long()))
        for i_node in node_list_only_sw:
            superCycle = flow_infos.superCycle_dic[i_node]
            i_flow = i_flow_dic[i_node]
            print('sw{} (cycle: {}) -> '.format(i_node, superCycle), end="")
            for i_win in range(flow_infos.numWin_dic[i_node][i_flow]):
                # real_open_time = m[open_time[i_node][i_flow][i_win]].as_long() % superCycle
                # real_close_time = m[close_time[i_node][i_flow][i_win]].as_long() % superCycle
                real_open_time = m[open_time[i_node][i_flow][i_win]].as_long()
                real_close_time = m[close_time[i_node][i_flow][i_win]].as_long()

                print(real_open_time, real_close_time, end="|")
            print("")
        # print("recv_time: " + str(m[recv_time[dst_node]].as_long() % cycle))
        print("recv_time: " + str(m[recv_time[dst_node]].as_long()))
        print("end_to_end latency: {}".format( \
            m[recv_time[dst_node]].as_long() - m[send_time[src_node]].as_long() \
        ))
        print("")

def output_result_yaml_sw(flow_infos, flow_list, times_for_gcl, m, output_filename):
    open_time = times_for_gcl.open_time
    close_time = times_for_gcl.close_time

    yaml_output = []
    for i_sw in flow_infos.sw_list:
        yaml_each_sw = {}
        superCycle = flow_infos.superCycle_dic[i_sw]
        yaml_each_sw["cycle"] = superCycle
        yaml_each_sw["name"] = i_sw

        yaml_controls = []
        isAdded = False
        for i_flow in range(flow_infos.numFlow_in_sw_dic[i_sw]):
            flow_id = get_flow_id_from_i_sw_and_i_flow(flow_list, i_sw, i_flow)

            all_open_close = []
            for i_win in range(flow_infos.numWin_dic[i_sw][i_flow]):
                real_open_time = m[open_time[i_sw][i_flow][i_win]].as_long() % superCycle
                real_close_time = m[close_time[i_sw][i_flow][i_win]].as_long() % superCycle
                one_open_close = [real_open_time, real_close_time, flow_id]
                all_open_close.append(one_open_close)

            # if the nextNode already exists in yaml_controls, add times to it
            nextNode = flow_infos.nextNode_in_sw_dic[i_sw][i_flow]
            for i_control, each_control_dic in enumerate(yaml_controls):
                if nextNode == each_control_dic["nextNode"]:
                    yaml_controls[i_control]["open_close"] += all_open_close
                    isAdded = True
                    break

            if not isAdded:
                yaml_each_control = {}
                yaml_each_control["nextNode"] = nextNode
                yaml_each_control["open_close"] = all_open_close
                yaml_controls.append(yaml_each_control)

            isAdded = False

        yaml_each_sw["control"] = yaml_controls

        yaml_output.append(yaml_each_sw)

    with open(output_filename, "w") as f:
        f.write(yaml.dump(yaml_output))

def output_result_yaml_cli_send(flow_list, times_for_gcl, m, output_filename):
    send_time = times_for_gcl.send_time

    yaml_output = []
    for each_flow in flow_list:
        flow_id = each_flow["flow_id"]
        src_node = each_flow["node_list"][0]
        pass_node_list = each_flow["node_list"][1:]
        cycle = each_flow["cycle"]
        size = each_flow["size"]
        real_send_time = m[send_time[src_node]].as_long() % cycle

        yaml_each_cli = { \
            "flow_id": flow_id, \
            "name": src_node, \
            "pass_node_list": pass_node_list, \
            "cycle": cycle, \
            "size": size, \
            "priority": 7, \
            "send_time": real_send_time}
        yaml_output.append(yaml_each_cli)

    with open(output_filename, "w") as f:
        f.write(yaml.dump(yaml_output))

def output_yaml_cli_recv(flow_list, output_filename):
    yaml_output = []
    for each_flow in flow_list:
        dst_node = each_flow["node_list"][-1]
        yaml_output.append({"name": dst_node})

    with open(output_filename, "w") as f:
        f.write(yaml.dump(yaml_output))

class Flow_infos:
    def __init__(self, flow_list):
        self.flow_list = flow_list

        self.cycleInSw_dic = gen_cycleInSw_dic(self.flow_list) # {0: [20, 30, 60], 1: [30, 60], 2: [30]}
        self.superCycle_dic = gen_superCycle_dic(self.cycleInSw_dic) # {0: 60, 1: 60, 2: 30}
        self.numWin_dic = gen_numWin_dic(self.cycleInSw_dic, self.superCycle_dic) # {0: [3, 2, 1], 1: [2, 1], 2: [1]}
        self.numFlow_in_sw_dic = gen_numFlow_in_sw_dic(self.cycleInSw_dic) # {0: 3, 1: 2, 2: 1}
        self.sw_list = gen_sw_list(self.cycleInSw_dic)
        self.num_sw = len(self.sw_list)
        self.nextNode_in_sw_dic = gen_nextNode_in_sw_dic(self.flow_list, self.numFlow_in_sw_dic)

class Times_for_gcl:
    def __init__(self, open_time, close_time, send_time, recv_time):
        self.open_time = open_time
        self.close_time = close_time
        self.send_time = send_time
        self.recv_time = recv_time

def main(external_flow_list):
    flow_list = get_flow_list_from_external_flow_list(external_flow_list)
    flow_infos = Flow_infos(flow_list)
    open_time, close_time = define_variables_sw(flow_infos)
    send_time, recv_time = define_variables_cli(flow_list)
    times_for_gcl = Times_for_gcl(open_time, close_time, send_time, recv_time)

    s = Solver()
    add_constraint(flow_list, flow_infos, times_for_gcl, s)
    m = check_solver(s)
    if m == UNSAT:
        return UNSAT

    # print_result_each_sw(flow_infos, times_for_gcl, m)
    # print("--------------------")
    # print_result_each_flow(flow_list, flow_infos, times_for_gcl, m)
    # print("====================")
    output_result_yaml_sw(flow_infos, flow_list, times_for_gcl, m, \
        '{}/workspace/test_z3/multiSw_sch/gcl_sw.yml'.format(home_dir))
    output_result_yaml_cli_send(flow_list, times_for_gcl, m, \
        '{}/workspace/test_z3/multiSw_sch/gcl_cli_send.yml'.format(home_dir))
    output_yaml_cli_recv(flow_list, \
        '{}/workspace/test_z3/multiSw_sch/cli_recv_list.yml'.format(home_dir))

    return SAT


if __name__ == "__main__":
    home_dir = os.path.expanduser('~')
    flow_with_path_filename = '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir)
    flow_list = get_flow_list_from_yaml(flow_with_path_filename)
    sat_or_unsat = main(flow_list)
    print("SAT" if sat_or_unsat == SAT else "UNSAT")