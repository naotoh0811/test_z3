import subprocess
import yaml

def read_yaml(filename):
    f = open(filename, "r+")
    data = yaml.load(f, yaml.SafeLoader)
    return data

def gen_csv_from_data(data, csv_filename):
    write_first_line(csv_filename)
    for flow in data:
        flow_id = flow["flow_id"]
        src = flow['src']
        dst = flow["dst"]
        cycle = flow["cycle"]
        payload = flow["payload"]
        header = 30
        size = payload + header if payload + header >= 72 else 72
        deadline = flow["deadline"]

        output = subprocess.run(["./main.o", str(src), str(dst)], stdout=subprocess.PIPE)
        # convert to str
        output = output.stdout.decode("utf8")
        # delete \n
        output = output.rstrip('\n')
        node_list_reverse = output.split()
        node_list = list(reversed(node_list_reverse))

        file_output = str(flow_id) + "," + str(cycle) + ","
        for node in node_list:
            file_output += node + " "
        file_output = file_output.rstrip(' ')
        file_output += "," + str(size) + "," + str(deadline) + "\n"

        with open(csv_filename, 'a') as f:
            f.write(file_output)

def write_first_line(csv_filename):
    with open(csv_filename, 'w'):
        pass
    with open(csv_filename, 'a') as f:
        f.write("flow_id,cycle,node_list,size,deadline\n")

if __name__ == "__main__":
    data = read_yaml('../flow/flow_hard.yml')
    gen_csv_from_data(data, 'flow_with_path.csv')
