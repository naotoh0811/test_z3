from z3 import *
import math
from functools import reduce
import pandas as pd

NOT_DEFINE = 1000

def lcm_base(x, y):
    return (x * y) // math.gcd(x, y)

def lcm(*numbers):
    return reduce(lcm_base, numbers, 1)

def lcm_list(numbers):
    return reduce(lcm_base, numbers, 1)

def csv_to_flow_info(filename):
    df = pd.read_csv(filename)
    flow_info = []
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

        flow_info.append({"name": name, "cycle": cycle, "node_list": node_list, "i_flow_dic": i_flow_dic, "ocu_time": ocu_time, "deadline": deadline})

    return flow_info

def gen_cycleInSw_dic(flow_info):
    num_flow = len(flow_info)
    cycleInSw_dic = {}
    for each_flow in flow_info:
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
        superCycle_dic[node] = lcm_list(cycles)

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

def gen_nextNode_in_sw_dic(flow_info, numFlow_in_sw_dic):
    nextNode_in_sw_dic = {}
    # init
    for (node, numFlow) in zip(numFlow_in_sw_dic.keys(), numFlow_in_sw_dic.values()):
        nextNode_in_sw_dic[node] = ["-"] * numFlow

    for each_flow in flow_info:
        node_list = each_flow["node_list"]
        node_list = node_list[1:]
        i_flow_dic = each_flow["i_flow_dic"]
        for i_node_list in range(len(node_list)-1):
            node = node_list[i_node_list]
            nextNode = node_list[i_node_list+1]
            i_flow = i_flow_dic[node]
            nextNode_in_sw_dic[node][i_flow] = nextNode

    return nextNode_in_sw_dic

link_delay = 10
flow_info = csv_to_flow_info("../network/dijkstra/flow_with_path.csv")
cycleInSw_dic = gen_cycleInSw_dic(flow_info) # {0: [20, 30, 60], 1: [30, 60], 2: [30]}
superCycle_dic = gen_superCycle_dic(cycleInSw_dic) # {0: 60, 1: 60, 2: 30}
numWin_dic = gen_numWin_dic(cycleInSw_dic, superCycle_dic) # {0: [3, 2, 1], 1: [2, 1], 2: [1]}
numFlow_in_sw_dic = gen_numFlow_in_sw_dic(cycleInSw_dic) # {0: 3, 1: 2, 2: 1}
num_sw = len(numFlow_in_sw_dic)
nextNode_in_sw_dic = gen_nextNode_in_sw_dic(flow_info, numFlow_in_sw_dic)

# define variable
## define open_time, close_time for sw
open_time = []
close_time = []
for i_node in range(num_sw):
    open_time.append([])
    close_time.append([])
    for i_flow in range(numFlow_in_sw_dic[i_node]):
        val_name_open = "open_time[" + str(i_node) + "][" + str(i_flow) + "]"
        val_name_close = "close_time[" + str(i_node) + "][" + str(i_flow) + "]"
        open_time[i_node].append(IntVector(val_name_open, numWin_dic[i_node][i_flow]))
        close_time[i_node].append(IntVector(val_name_close, numWin_dic[i_node][i_flow]))

## define send_time, recv_time for cli
send_time = {}
recv_time = {}
for each_flow in flow_info:
    node_list = each_flow["node_list"]
    src_node = node_list[0]
    dst_node = node_list[-1]
    val_name_send = "send_time[" + str(src_node) +"]"
    val_name_recv = "recv_time[" + str(dst_node) +"]"
    send_time[src_node] = Int(val_name_send)
    recv_time[dst_node] = Int(val_name_recv)

s = Solver()

for each_flow in flow_info:
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
    for i_node in node_list_only_sw:
        i_flow = i_flow_dic[i_node]
        superCycle = superCycle_dic[i_node]

        for i_win in range(numWin_dic[i_node][i_flow]):
            # fisrt window > 0
            if i_win == 0:
                s.add(open_time[i_node][i_flow][i_win] >= 0)
            
            # cycle time

            # if i_win != numWin_dic[i_node][i_flow] - 1:
            #     s.add(open_time[i_node][i_flow][i_win+1] - open_time[i_node][i_flow][i_win] == cycle)
            # else: # last win
            #     s.add( (superCycle - open_time[i_node][i_flow][i_win]) + (open_time[i_node][i_flow][0] - 0) == cycle )
            #     # last window < superCycle
            #     s.add(close_time[i_node][i_flow][i_win] <= superCycle)

            # if i_win != numWin_dic[i_node][i_flow] - 1: # not last
            #     s.add(Or(open_time[i_node][i_flow][i_win+1] - open_time[i_node][i_flow][i_win] == cycle, (superCycle - open_time[i_node][i_flow][i_win]) + open_time[i_node][i_flow][i_win+1] == cycle))
            # else: # last win
            #     s.add(Or(open_time[i_node][i_flow][0] - open_time[i_node][i_flow][i_win] == cycle, (superCycle - open_time[i_node][i_flow][i_win]) + open_time[i_node][i_flow][0] == cycle))

            if i_win == 0: # fisrt win
                s.add(open_time[i_node][i_flow][i_win] - send_time[src_node] >= link_delay)
            if i_win != numWin_dic[i_node][i_flow] - 1: # not first, last
                s.add(open_time[i_node][i_flow][i_win+1] - open_time[i_node][i_flow][i_win] == cycle)
            else: # last win
                # 最悪の場合 (closeの瞬間に転送)を想定
                s.add(recv_time[dst_node] - close_time[i_node][i_flow][i_win] >= link_delay)
                # これがないと計算時間が無限になる
                # 精々2サイクル分くらいで十分か
                s.add(close_time[i_node][i_flow][i_win] < superCycle*2)

            # exclusivenessの制約付与の際にこれがないと不具合
            # 正直、適切でない
            s.add(close_time[i_node][i_flow][i_win] % superCycle != 0)

            # 0 < time < superCycle
            # s.add(open_time[i_node][i_flow][i_win] >= 0)
            # s.add(close_time[i_node][i_flow][i_win] <= superCycle)
            
            # occupancy time
            s.add(close_time[i_node][i_flow][i_win] - open_time[i_node][i_flow][i_win] == ocu_time)

        # 0 > time
        s.add(send_time[src_node] >= 0)

        # next node
        if prev_i_node != NOT_DEFINE: # not first sw
            # s.add(Or(open_time[i_node][i_flow][0] - close_time[prev_i_node][prev_i_flow][0] >= link_delay, open_time[i_node][i_flow][0] + (superCycle - close_time[prev_i_node][prev_i_flow][0]) >= link_delay))
            s.add(open_time[i_node][i_flow][0] - close_time[prev_i_node][prev_i_flow][0] >= link_delay)
        # else: # first sw
        #     s.add(Or(open_time[i_node][i_flow][0] - send_time[src_node] >= link_delay, open_time[i_node][i_flow][0] + (superCycle - send_time[src_node]) >= link_delay))

        prev_i_node = i_node
        prev_i_flow = i_flow

    # deadline
    s.add(recv_time[dst_node] - send_time[src_node] <= deadline)

# exclusiveness
for i_sw in range(num_sw): # 0,1,2  sw_dicを作って回したほうがいいか
    superCycle = superCycle_dic[i_sw]
    for i_flow in range(numFlow_in_sw_dic[i_sw]): # i_sw=0なら0,1,2
        nextNode = nextNode_in_sw_dic[i_sw][i_flow]
        for i_win in range(numWin_dic[i_sw][i_flow]): #[0][0]なら0,1,2
            # each win to another win
            for i2_flow in range(numFlow_in_sw_dic[i_sw]):
                nextNode2 = nextNode_in_sw_dic[i_sw][i2_flow]
                # apply exclusiveness only when the next nodes of i,i2 are equal
                if i_flow >= i2_flow or nextNode != nextNode2:
                    continue
                for i2_win in range(numWin_dic[i_sw][i2_flow]):
                    s.add(Or( \
                        close_time[i_sw][i_flow][i_win] % superCycle <= open_time[i_sw][i2_flow][i2_win] % superCycle, \
                        open_time[i_sw][i_flow][i_win] % superCycle >= close_time[i_sw][i2_flow][i2_win] % superCycle \
                    ))


r = s.check()
if r == sat:
    m = s.model()
else:
    print(r)
    exit()


for (i_o, i_c) in zip(open_time, close_time):
    for (j_o, j_c) in zip(i_o, i_c):
        for (k_o, k_c) in zip(j_o, j_c):
            print(m[k_o], m[k_c], end="|")
        print("")
    print("")

# for (i_o, i_c) in zip(open_time, close_time):
#     for (j_o, j_c) in zip(i_o, i_c):
#         prev_close = 0
#         for (k_o, k_c) in zip(j_o, j_c):
#             t_o = m[k_o].as_long()
#             t_c = m[k_c].as_long()
#             print("-" * (t_o - prev_close), end="")
#             print("+" * (t_c - t_o), end="")
#             prev_close = t_c
#         print("")
#     print("")

for each_flow in flow_info:
    node_list = each_flow["node_list"]
    src_node = node_list[0]
    dst_node = node_list[-1]
    node_list_only_sw = node_list[1:-1]
    cycle = each_flow["cycle"]
    i_flow_dic = each_flow["i_flow_dic"]
    ocu_time = each_flow["ocu_time"]
    
    print(m[send_time[src_node]])
    for i_node in node_list_only_sw:
        superCycle = superCycle_dic[i_node]
        i_flow = i_flow_dic[i_node]
        for i_win in range(numWin_dic[i_node][i_flow]):
            # real_open_time = m[open_time[i_node][i_flow][i_win]].as_long() % superCycle
            # real_close_time = m[close_time[i_node][i_flow][i_win]].as_long() % superCycle
            real_open_time = m[open_time[i_node][i_flow][i_win]].as_long()
            real_close_time = m[close_time[i_node][i_flow][i_win]].as_long()

            print(real_open_time, real_close_time, end="|")
        print("")
    print(m[recv_time[dst_node]])
    print("")
    