import pandas as pd
import random
import yaml
import math
import sys
import os.path

def get_cli_list_from_csv(filename):
    df = pd.read_csv(filename)
    for row in df.itertuples():
        cli_list = row.cli.split()
        sw_list = row.sw.split()
    cli_list = [int(i) for i in cli_list]
    sw_list = [int(i) for i in sw_list]
    return cli_list, sw_list

def gen_flow(num_flow, node_filename, output_filename):
    cli_list, sw_list = get_cli_list_from_csv(node_filename)

    sw_num = len(sw_list)
    max_link_num = sw_num + 1
    link_bandwidth = 100
    light_speed = 5 * (10 ** -3)

    cli_num = len(cli_list)
    #num_flow = 10
    if num_flow > cli_num // 2:
        print("WARNING: num_flow is too large. Now set num_flow to {}".format(cli_num // 2))
        num_flow = cli_num // 2

    flow_dic_list = []
    flow_id = 0
    for i in range(num_flow):
        src_node = random.choice(cli_list)
        cli_list = [val for val in cli_list if val != src_node]
        dst_node = random.choice(cli_list)
        cli_list = [val for val in cli_list if val != dst_node]

        # cycle = random.choice([100, 200, 300, 400, 600])
        cycle = random.choice([100, 200, 400])
        payload = 46
        min_deadline = \
            math.ceil((payload + 30) * 8 / link_bandwidth + light_speed * 10) * max_link_num
        deadline = random.randint(min_deadline, 100)
        deadline = random.randint(min_deadline*2, min_deadline*3)
        deadline = 200
        flow_dic = { \
            "flow_id": flow_id, \
            "src": src_node, \
            "dst": dst_node, \
            "cycle": cycle, \
            "payload": payload, \
            "deadline": deadline}
        flow_dic_list.append(flow_dic)
        flow_id += 1

    with open(output_filename, "w") as f:
        f.write(yaml.dump(flow_dic_list))

def main(num_flow):
    home_dir = os.path.expanduser('~')
    gen_flow( \
        num_flow, \
        '{}/workspace/test_z3/network/network/node.csv'.format(home_dir), \
        '{}/workspace/test_z3/network/flow/flow_hard.yml'.format(home_dir))


if __name__ == "__main__":
    num_flow = 3
    if len(sys.argv) == 2:
        num_flow = int(sys.argv[1])
    else:
        print("WARNING: arg is invalid. Now set num_flow to 3.")

    main(num_flow)