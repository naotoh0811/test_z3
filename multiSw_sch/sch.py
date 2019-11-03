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
    for row in df.itertuples():
        name = row.name
        cycle = int(row.cycle)
        node_list = row.node_list.split()
        node_list = [int(i) for i in node_list]
        i_flow_list = row.i_flow_list.split()
        i_flow_list = [int(i) for i in i_flow_list]
        ocu_time = row.ocu_time
        flow_info.append({"name": name, "cycle": cycle, "node_list": node_list, "i_flow_list": i_flow_list, "ocu_time": ocu_time})

    return flow_info

def gen_cycleInSw_dic(flow_info):
    num_flow = len(flow_info)
    cycleInSw_dic = {}
    for each_flow in flow_info:
        for node in each_flow["node_list"]:
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

link_delay = 5
flow_info = csv_to_flow_info("flow.csv")
cycleInSw_dic = gen_cycleInSw_dic(flow_info) # {0: [20, 30, 60], 1: [30, 60], 2: [30]}
superCycle_dic = gen_superCycle_dic(cycleInSw_dic) # {0: 60, 1: 60, 2: 30}
numWin_dic = gen_numWin_dic(cycleInSw_dic, superCycle_dic) # {0: [3, 2, 1], 1: [2, 1], 2: [1]}
numFlow_in_sw_dic = gen_numFlow_in_sw_dic(cycleInSw_dic) # {0: 3, 1: 2, 2: 1}
num_sw = len(numFlow_in_sw_dic)

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

s = Solver()

for each_flow in flow_info:
    node_list = each_flow["node_list"]
    cycle = each_flow["cycle"]
    i_flow_list = each_flow["i_flow_list"]
    ocu_time = each_flow["ocu_time"]
    prev_i_node = NOT_DEFINE
    prev_i_flow = NOT_DEFINE
    for (i_node, i_flow) in zip(node_list, i_flow_list):
        superCycle = superCycle_dic[i_node]

        for i_win in range(numWin_dic[i_node][i_flow]):
            # fisrt window > 0
            if i_win == 0:
                s.add(open_time[i_node][i_flow][i_win] >= 0)
            
            # cycle time
            if i_win != numWin_dic[i_node][i_flow] - 1:
                s.add(open_time[i_node][i_flow][i_win+1] - open_time[i_node][i_flow][i_win] == cycle)
            else: # last win
                s.add( (superCycle - open_time[i_node][i_flow][i_win]) + (open_time[i_node][i_flow][0] - 0) == cycle )
                # last window < superCycle
                s.add(close_time[i_node][i_flow][i_win] <= superCycle)
            
            # occupancy time
            s.add(close_time[i_node][i_flow][i_win] - open_time[i_node][i_flow][i_win] == ocu_time)

        # next node
        if prev_i_node != NOT_DEFINE:
            s.add(open_time[i_node][i_flow][0] - open_time[prev_i_node][prev_i_flow][0] == link_delay)

        prev_i_node = i_node
        prev_i_flow = i_flow

# exclusiveness
for i_sw in range(num_sw): # 0,1,2
    for i_flow in range(numFlow_in_sw_dic[i_sw]): # i_sw=0なら0,1,2
        for i_win in range(numWin_dic[i_sw][i_flow]): #[0][0]なら0,1,2
            for i2_flow in range(numFlow_in_sw_dic[i_sw]):
                for i2_win in range(numWin_dic[i_sw][i2_flow]):
                    if i_flow < i2_flow:
                        s.add(Or(close_time[i_sw][i_flow][i_win] <= open_time[i_sw][i2_flow][i2_win], open_time[i_sw][i_flow][i_win] >= close_time[i_sw][i2_flow][i2_win]))

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

for (i_o, i_c) in zip(open_time, close_time):
    for (j_o, j_c) in zip(i_o, i_c):
        prev_close = 0
        for (k_o, k_c) in zip(j_o, j_c):
            t_o = m[k_o].as_long()
            t_c = m[k_c].as_long()
            print("-" * (t_o - prev_close), end="")
            print("+" * (t_c - t_o), end="")
            prev_close = t_c
        print("")
    print("")