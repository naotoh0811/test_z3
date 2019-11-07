from z3 import *
import pandas as pd
import yaml
import lcm

NOT_DEFINE = 1000

def get_flow_list_from_csv(filename):
    df = pd.read_csv(filename)
    flow_list = []
    i_flow_dic_cum = {}
    for row in df.itertuples():
        name = row.name
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

        ocu_time = row.ocu_time
        deadline = row.deadline

        flow_list.append({"name": name, "cycle": cycle, "node_list": node_list, "i_flow_dic": i_flow_dic, "ocu_time": ocu_time, "deadline": deadline})

    return flow_list

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

def define_variables_sw(flow_infos):
    ## define open_time, close_time for sw
    open_time = []
    close_time = []
    for i_node in range(flow_infos.num_sw):
        open_time.append([])
        close_time.append([])
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

def add_constraint(flow_list, flow_info, s):
    for each_flow in flow_list:
        node_list = each_flow["node_list"]
        src_node = node_list[0]
        dst_node = node_list[-1]
        node_list_only_sw = node_list[1:-1]
        cycle = each_flow["cycle"]
        i_flow_dic = each_flow["i_flow_dic"]
        ocu_time = each_flow["ocu_time"]
        deadline = each_flow["deadline"]
        prev_i_node = NOT_DEFINE
        prev_i_flow = NOT_DEFINE

        # 0 > time
        s.add(send_time[src_node] >= 0)
        # deadline
        s.add(recv_time[dst_node] - send_time[src_node] <= deadline-1)

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
                else: # last win
                    # 最悪の場合 (closeの瞬間に転送)を想定
                    s.add(recv_time[dst_node] - close_time[i_node][i_flow][i_win] >= link_delay)
                    # これがないと計算時間が無限になる
                    # 精々2サイクル分くらいで十分か
                    s.add(close_time[i_node][i_flow][i_win] < superCycle*2)

                # window does not stride over cycle end point
                # exclusivenessの制約付与の際にこれがないと不具合
                # 正直、適切でない
                s.add(open_time[i_node][i_flow][i_win] % superCycle < close_time[i_node][i_flow][i_win] % superCycle)

                # occupancy time
                s.add(close_time[i_node][i_flow][i_win] - open_time[i_node][i_flow][i_win] == ocu_time)

            if i_node == node_list_only_sw[0]: # first sw
                # from src_node
                s.add(open_time[i_node][i_flow][i_win] - send_time[src_node] >= link_delay)
            else: # not first sw
                if i_node == node_list_only_sw[-1]: # last sw
                    # to dst_node
                    # 最悪の場合 (closeの瞬間に転送)を想定
                    s.add(recv_time[dst_node] - close_time[i_node][i_flow][i_last_win] >= link_delay)
                    # これがないと計算時間が無限になる
                    # 精々2サイクル分くらいで十分か
                    s.add(close_time[i_node][i_flow][i_last_win] < superCycle*2)

                # next node
                s.add(open_time[i_node][i_flow][0] - close_time[prev_i_node][prev_i_flow][0] >= link_delay)

            prev_i_node = i_node
            prev_i_flow = i_flow

    # exclusiveness
    for i_sw in range(flow_infos.num_sw): # 0,1,2  sw_dicを作って回したほうがいいか
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
        print(r)
        exit()

def print_result_each_sw(flow_infos, m):
    for i_sw in range(flow_infos.num_sw):
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

def print_result_each_flow(flow_list, flow_infos, m):
    for each_flow in flow_list:
        name = each_flow["name"]
        node_list = each_flow["node_list"]
        src_node = node_list[0]
        dst_node = node_list[-1]
        node_list_only_sw = node_list[1:-1]
        cycle = each_flow["cycle"]
        i_flow_dic = each_flow["i_flow_dic"]
        ocu_time = each_flow["ocu_time"]
        
        print(name + ": ")
        print("send_time: " + str(m[send_time[src_node]].as_long()))
        for i_node in node_list_only_sw:
            superCycle = flow_infos.superCycle_dic[i_node]
            i_flow = i_flow_dic[i_node]
            for i_win in range(flow_infos.numWin_dic[i_node][i_flow]):
                real_open_time = m[open_time[i_node][i_flow][i_win]].as_long() % superCycle
                real_close_time = m[close_time[i_node][i_flow][i_win]].as_long() % superCycle
                # real_open_time = m[open_time[i_node][i_flow][i_win]].as_long()
                # real_close_time = m[close_time[i_node][i_flow][i_win]].as_long()

                print(real_open_time, real_close_time, end="|")
            print("")
        print("recv_time: " + str(m[recv_time[dst_node]].as_long()))
        print("")

def output_result_yaml_sw(flow_infos, m, output_filename):
    yaml_output = []
    for i_sw in range(flow_infos.num_sw):
        yaml_each_sw = {}
        superCycle = flow_infos.superCycle_dic[i_sw]
        yaml_each_sw["name"] = i_sw

        yaml_controls = []
        isAdded = False
        for i_flow in range(flow_infos.numFlow_in_sw_dic[i_sw]):

            all_open_close = []
            for i_win in range(flow_infos.numWin_dic[i_sw][i_flow]):
                real_open_time = m[open_time[i_sw][i_flow][i_win]].as_long() % superCycle
                real_close_time = m[close_time[i_sw][i_flow][i_win]].as_long() % superCycle
                one_open_close = [real_open_time, real_close_time]
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

        yaml_each_sw["control"] = yaml_controls

        yaml_output.append(yaml_each_sw)

    f = open(output_filename, "w")
    f.write(yaml.dump(yaml_output))

def output_result_yaml_cli(flow_list, m, output_filename):
    yaml_output = []
    for each_flow in flow_list:
        src_node = each_flow["node_list"][0]
        cycle = each_flow["cycle"]
        real_send_time = m[send_time[src_node]].as_long()

        yaml_each_cli = {"name": src_node, "cycle": cycle, "send": real_send_time}
        yaml_output.append(yaml_each_cli)

    f = open(output_filename, "w")
    f.write(yaml.dump(yaml_output))

class Flow_infos:
    def __init__(self, flow_list):
        self.flow_list = flow_list;

        self.cycleInSw_dic = gen_cycleInSw_dic(self.flow_list) # {0: [20, 30, 60], 1: [30, 60], 2: [30]}
        self.superCycle_dic = gen_superCycle_dic(self.cycleInSw_dic) # {0: 60, 1: 60, 2: 30}
        self.numWin_dic = gen_numWin_dic(self.cycleInSw_dic, self.superCycle_dic) # {0: [3, 2, 1], 1: [2, 1], 2: [1]}
        self.numFlow_in_sw_dic = gen_numFlow_in_sw_dic(self.cycleInSw_dic) # {0: 3, 1: 2, 2: 1}
        self.num_sw = len(self.numFlow_in_sw_dic)
        self.nextNode_in_sw_dic = gen_nextNode_in_sw_dic(self.flow_list, self.numFlow_in_sw_dic)


if __name__ == "__main__":
    flow_list = get_flow_list_from_csv("../network/dijkstra/flow_with_path.csv")
    flow_infos = Flow_infos(flow_list)
    link_delay = 10
    open_time, close_time = define_variables_sw(flow_infos)
    send_time, recv_time = define_variables_cli(flow_list)

    s = Solver()
    add_constraint(flow_list, flow_infos, s)
    m = check_solver(s)

    print_result_each_sw(flow_infos, m)
    print("--------------------")
    print_result_each_flow(flow_list, flow_infos, m)
    output_result_yaml_sw(flow_infos, m, 'gcl_sw.yml')
    output_result_yaml_cli(flow_list, m, 'gcl_cli.yml')