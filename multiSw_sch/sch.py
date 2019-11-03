from z3 import *
import math
from functools import reduce

NOT_DEFINE = 1000

def lcm_base(x, y):
    return (x * y) // math.gcd(x, y)

def lcm(*numbers):
    return reduce(lcm_base, numbers, 1)

def lcm_list(numbers):
    return reduce(lcm_base, numbers, 1)

link_delay = 5
flow_info = [{"name": "flow0", "cycle": 20, "node_list": [0], "i_flow_list": [0], "ocu_time": 1},
             {"name": "flow1", "cycle": 30, "node_list": [0,1,2], "i_flow_list": [1,0,0], "ocu_time": 1},
             {"name": "flow2", "cycle": 60, "node_list": [0,1], "i_flow_list": [2,1], "ocu_time": 1}]
cycle_in_sw = [[20, 30, 60], [30, 60], [30]]
superCycle_in_sw = [lcm_list(cycles) for cycles in cycle_in_sw] # [60, 60, 30]
num_win = [] # [[3,2,1], [2,1], [1]]
for i, cycles in enumerate(cycle_in_sw):
    num_win.append([])
    for cycle in cycles:
        num_win[i].append(int(superCycle_in_sw[i] / cycle))
num_flow_in_sw = [len(num) for num in cycle_in_sw] # [3, 2, 1]
num_sw = len(num_flow_in_sw)
open_time = []
close_time = []
for i in range(num_sw):
    open_time.append([])
    close_time.append([])
    for j in range(num_flow_in_sw[i]):
        num_win_tmp = int(superCycle_in_sw[i] / cycle_in_sw[i][j])
        val_name_open = "open_time[" + str(i) + "][" + str(j) + "]"
        val_name_close = "close_time[" + str(i) + "][" + str(j) + "]"
        open_time[i].append(IntVector(val_name_open, num_win_tmp))
        close_time[i].append(IntVector(val_name_close,num_win_tmp))

s = Solver()

for each_flow in flow_info:
    node_list = each_flow["node_list"]
    cycle = each_flow["cycle"]
    i_flow_list = each_flow["i_flow_list"]
    ocu_time = each_flow["ocu_time"]
    prev_i_node = NOT_DEFINE
    prev_i_flow = NOT_DEFINE
    for (i_node, i_flow) in zip(node_list, i_flow_list):
        superCycle = superCycle_in_sw[i_node]
        #num_win = int(superCycle / cycle)

        for i_win in range(num_win[i_node][i_flow]):
            # fisrt window > 0
            if i_win == 0:
                s.add(open_time[i_node][i_flow][i_win] >= 0)
            
            # cycle time
            if i_win != num_win[i_node][i_flow] - 1:
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
    for i_flow in range(num_flow_in_sw[i_sw]): # i_sw=0なら0,1,2
        for i_win in range(num_win[i_sw][i_flow]): #[0][0]なら0,1,2
            for i2_flow in range(num_flow_in_sw[i_sw]):
                for i2_win in range(num_win[i_sw][i2_flow]):
                    if i_flow < i2_flow:
                        #print(str(i_sw) + str(i_flow) + str(i_win) + " " + str(i_sw) + str(i2_flow) + str(i2_win))
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