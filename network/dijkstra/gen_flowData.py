import subprocess
import yaml
import random
import math
import os
import sys
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import network.dijkstra.dijkstra as dijkstra

link_bandwidth = 1000 # in Mbps
light_speed = 5 * (10 ** -3)
header = 30

def read_yaml(filename):
    f = open(filename, "r+")
    data = yaml.load(f, yaml.SafeLoader)
    return data

def get_path_by_dijkstra_cpp(src, dst): # not used
    home_dir = os.path.expanduser('~')
    output = subprocess.run( \
        ['{}/workspace/test_z3/network/dijkstra/main.o'.format(home_dir), str(src), str(dst)], \
        stdout=subprocess.PIPE)
    # convert to str
    output = output.stdout.decode("utf8")
    # delete \n
    output = output.rstrip('\n')
    node_list_reverse = output.split()
    node_list = list(reversed(node_list_reverse))

    return node_list

def get_transferLatency(payload):
    # payload: 1500 -> return 12.29
    # return math.ceil((payload + header) * 8 / link_bandwidth + light_speed * 10)
    return (payload + header) * 8 / link_bandwidth + light_speed * 10

def gen_flowWithPath_from_data(data, yaml_filename_hard, yaml_filename_soft):
    flow_dic_list_hard = []
    flow_dic_list_soft = []
    for each_flow in data:
        flow_id = each_flow["flow_id"]
        src = each_flow['src']
        dst = each_flow["dst"]
        cycle = each_flow["cycle"]
        payload = each_flow["payload"]
        size = payload + header if payload + header >= 72 else 72

        # get node_list by using dijkstra
        node_list = dijkstra.main(src, dst)
        num_hop = len(node_list) - 1
        minLatency = get_transferLatency(payload) * num_hop
        minLatency_ceil = math.ceil(get_transferLatency(payload)) * num_hop
        # minData_transferLatency = get_transferLatency(46)

        if each_flow["kind"] == 'hard': # hard flow
            # set deadline
            # deadline = random.randint(math.ceil(minLatency*4), math.ceil(minLatency*4))
            deadline = math.ceil(minLatency*1.1)

            flow_dic = { \
                "flow_id": flow_id, \
                "cycle": cycle, \
                "node_list": node_list, \
                "size": size, \
                "deadline": deadline \
            }
            flow_dic_list_hard.append(flow_dic)
        else: # soft flow
            # set TUF
            first_val = 100
            # first_val = random.randint(30, 200)

            # dec_point = minLatency*1
            dec_point = minLatency_ceil * 1.1

            # x_intercept = random.randint(math.ceil(minLatency*4.3), math.ceil(minLatency*4.5))
            # x_intercept = \
            #     dec_point + minData_transferLatency * random.randint(10, 50) # dec_point + (6~30)
            x_intercept = float(dec_point + \
                # get_transferLatency(1500) * random.randint(1, 5)) # dec_point + (12~60)
                random.randint(
                    math.ceil(get_transferLatency(1500)),
                    # math.ceil(get_transferLatency(1500)) * 5)
                    math.ceil(get_transferLatency(1500)) * 10)
            )

            slope = first_val / (dec_point - x_intercept)
            y_intercept = -slope * x_intercept
            tuf_list = [ \
                [0, dec_point, "linear", 0, first_val], \
                [dec_point, x_intercept, "linear", slope, y_intercept] \
            ]

            flow_dic = { \
                "flow_id": flow_id, \
                "cycle": cycle, \
                "node_list": node_list, \
                "size": size, \
                "dec_point": dec_point, \
                "tuf": tuf_list \
            }
            flow_dic_list_soft.append(flow_dic)

    if flow_dic_list_hard == []:
        if os.path.exists(yaml_filename_hard):
            os.remove(yaml_filename_hard)
    else:
        with open(yaml_filename_hard, "w") as f:
            f.write(yaml.dump(flow_dic_list_hard))

    if flow_dic_list_soft == []:
        if os.path.exists(yaml_filename_soft):
            os.remove(yaml_filename_soft)
    else:
        with open(yaml_filename_soft, "w") as f:
            f.write(yaml.dump(flow_dic_list_soft))

def write_first_line(csv_filename): # not used
    with open(csv_filename, 'w'):
        pass
    with open(csv_filename, 'a') as f:
        f.write("flow_id,cycle,node_list,size,deadline\n")

def main():
    home_dir = os.path.expanduser('~')
    data = read_yaml('{}/workspace/test_z3/network/flow/flow.yml'.format(home_dir))
    gen_flowWithPath_from_data(data, \
    '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir), \
    '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir))


if __name__ == "__main__":
    main()