import subprocess
import yaml
import os.path
import sys
home_dir = os.path.expanduser('~')
sys.path.append('{}/workspace/test_z3'.format(home_dir))
import network.dijkstra.dijkstra as dijkstra

def read_yaml(filename):
    f = open(filename, "r+")
    data = yaml.load(f, yaml.SafeLoader)
    return data

def get_path_by_dijkstra_cpp(src, dst):
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

def gen_csv_from_data(data, yaml_filename_hard, yaml_filename_soft):
    flow_dic_list_hard = []
    flow_dic_list_soft = []
    for each_flow in data:
        flow_id = each_flow["flow_id"]
        src = each_flow['src']
        dst = each_flow["dst"]
        cycle = each_flow["cycle"]
        payload = each_flow["payload"]
        header = 30
        size = payload + header if payload + header >= 72 else 72

        node_list = dijkstra.main(src, dst)

        if "deadline" in each_flow: # hard flow
            deadline = each_flow["deadline"]
            flow_dic = { \
                "flow_id": flow_id, \
                "cycle": cycle, \
                "node_list": node_list, \
                "size": size, \
                "deadline": deadline}
            flow_dic_list_hard.append(flow_dic)
        else: # soft flow
            dec_point = each_flow["dec_point"]
            tuf = each_flow["tuf"]
            flow_dic = { \
                "flow_id": flow_id, \
                "cycle": cycle, \
                "node_list": node_list, \
                "size": size, \
                "dec_point": dec_point, \
                "tuf": tuf}
            flow_dic_list_soft.append(flow_dic)

    with open(yaml_filename_hard, "w") as f:
        f.write(yaml.dump(flow_dic_list_hard))
    with open(yaml_filename_soft, "w") as f:
        f.write(yaml.dump(flow_dic_list_soft))

def write_first_line(csv_filename):
    with open(csv_filename, 'w'):
        pass
    with open(csv_filename, 'a') as f:
        f.write("flow_id,cycle,node_list,size,deadline\n")

def main():
    home_dir = os.path.expanduser('~')
    data = read_yaml('{}/workspace/test_z3/network/flow/flow.yml'.format(home_dir))
    gen_csv_from_data(data, \
    '{}/workspace/test_z3/network/dijkstra/flow_with_path_hard.yml'.format(home_dir), \
    '{}/workspace/test_z3/network/dijkstra/flow_with_path_soft.yml'.format(home_dir))


if __name__ == "__main__":
    main()