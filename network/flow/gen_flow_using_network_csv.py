import pandas as pd
import random
import yaml
import math
import sys
import os.path
import copy

link_bandwidth = 1000 # in Mbps
light_speed = 5 * (10 ** -3)

def get_node_list_from_csv(filename):
    df = pd.read_csv(filename)
    for row in df.itertuples():
        cli_list = row.cli.split()
        sw_list = row.sw.split()
    cli_list = [int(i) for i in cli_list]
    sw_list = [int(i) for i in sw_list]
    return cli_list, sw_list

def get_node_pair_random(cli_list, num_flow):
    remaining_cli_list = copy.deepcopy(cli_list)

    node_pair_list = []
    for i in range(num_flow):
        src_node = random.choice(remaining_cli_list)
        remaining_cli_list = [node for node in remaining_cli_list if node != src_node]
        dst_node = random.choice(remaining_cli_list)
        remaining_cli_list = [node for node in remaining_cli_list if node != dst_node]

        node_pair_list.append((src_node, dst_node))
    
    return node_pair_list

def get_node_pair_static(cli_list, num_flow):
    src_node = cli_list[0]
    dst_node = cli_list[0 + 4]
    node_pair_list = []
    for i in range(num_flow):
        node_pair_list.append((src_node, dst_node))

    return node_pair_list

def get_node_pair_samePath(cli_list, num_flow, num_sw, num_pass_sw):
    num_cli_for_each_sw = int(len(cli_list) / num_sw)
    if num_flow > num_cli_for_each_sw:
        raise Exception('num_flow exceeds num_cli_for_each_sw.')
    if num_pass_sw > num_sw:
        raise Exception('num_pass_sw exceeds num_sw.')
    
    node_pair_list = []
    for i in range(num_flow):
        src_node = cli_list[0 + i]
        dst_node = cli_list[0 + i + num_cli_for_each_sw * (num_pass_sw - 1)]
        node_pair_list.append((src_node, dst_node))
    
    return node_pair_list

def get_flow_property_fixed_bandwidth(num_flow_soft, fixed_bandwidth):
    cycle = 50
    while True:
        payload = math.ceil((fixed_bandwidth * cycle / 8) / num_flow_soft - 30)
        if payload <= 1500:
            break
        else:
            cycle /= 2

    return cycle, payload

def get_payload_from_flow_property(num_flow_soft, fixed_bandwidth, cycle):
    payload = math.ceil((fixed_bandwidth * cycle / 8) / num_flow_soft - 30)
    if payload > 1500 or payload < 46:
        raise Exception('Payload size is invalid.')
    return payload

def gen_flow(num_flow, num_flow_soft, num_pass_sw, fixed_bandwidth, cycle_soft, node_filename, output_filename):
    cli_list, sw_list = get_node_list_from_csv(node_filename)

    num_sw = len(sw_list)

    num_cli = len(cli_list)
    if num_flow > num_cli // 2:
        print("WARNING: num_flow is too large. Now set num_flow to {}".format(num_cli // 2))
        num_flow = num_cli // 2

    # node_pair_list = get_node_pair_random(cli_list, num_flow)
    node_pair_list = get_node_pair_samePath(cli_list, num_flow, num_sw, num_pass_sw)

    flow_dic_list = []
    for i in range(num_flow):
        # set src/dst node
        (src_node, dst_node) = node_pair_list[i]

        # cycle = random.choice([100, 200, 300, 400, 600])
        # cycle = random.choice([50, 100, 200, 400])

        if i < num_flow_soft: # soft flow
            # cycle = random.choice([50, 100])
            # cycle = 100
            # payload = random.randint(1500, 1500) # 46 -- 1500
            # cycle, payload = get_flow_property_fixed_bandwidth(num_flow_soft, fixed_bandwidth)
            payload = get_payload_from_flow_property(num_flow_soft, fixed_bandwidth, cycle_soft)

            flow_dic = { \
                "flow_id": i, \
                "src": src_node, \
                "dst": dst_node, \
                "cycle": cycle_soft, \
                "payload": payload, \
                "kind": 'soft'
                # "tuf": tuf_list, \
                # "dec_point": dec_point \
            }
        else: # hard flow
            # cycle = random.choice([200, 400])
            # cycle = 200 if i % 2 == 0 else 400
            cycle = 400
            # cycle_list = [100, 100, 200]
            # cycle = cycle_list[i - 2]
            payload = random.randint(1500, 1500) # 46 -- 1500

            flow_dic = { \
                "flow_id": i, \
                "src": src_node, \
                "dst": dst_node, \
                "cycle": cycle, \
                "payload": payload, \
                "kind": 'hard'
                # "deadline": deadline
            }

        flow_dic_list.append(flow_dic)

    with open(output_filename, "w") as f:
        f.write(yaml.dump(flow_dic_list))

def main(num_flow, num_flow_soft, num_pass_sw, fixed_bandwidth, cycle_soft):
    home_dir = os.path.expanduser('~')
    gen_flow( \
        num_flow, \
        num_flow_soft, \
        num_pass_sw, \
        fixed_bandwidth, \
        cycle_soft, \
        '{}/workspace/test_z3/network/network/node.csv'.format(home_dir), \
        '{}/workspace/test_z3/network/flow/flow.yml'.format(home_dir))


if __name__ == "__main__":
    num_flow = 3
    num_flow_soft = 2
    num_pass_sw = 5
    fixed_bandwidth = 900
    cycle_soft = 50
    if len(sys.argv) == 6:
        num_flow = int(sys.argv[1])
        num_flow_soft = int(sys.argv[2])
        num_pass_sw = int(sys.argv[3])
        fixed_bandwidth = int(sys.argv[4])
        cycle_soft = int(sys.argv[5])
    else:
        print("WARNING: arg is invalid. Now set num_flow to 3, num_flow_soft to 2.")

    main(num_flow, num_flow_soft, num_pass_sw, fixed_bandwidth, cycle_soft)