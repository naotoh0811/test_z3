import subprocess
import yaml

def read_yaml(filename):
    f = open(filename, "r+")
    data = yaml.load(f, yaml.SafeLoader)
    return data

def gen_csv_from_data(data, csv_filename):
    write_first_line(csv_filename)
    for flow in data:
        name = flow["name"]
        src = flow['src']
        dst = flow["dst"]
        cycle = flow["cycle"]
        size = flow["size"]
        deadline = flow["deadline"]

        output = subprocess.run(["./main.o", str(src), str(dst)], stdout=subprocess.PIPE)
        # convert to str
        output = output.stdout.decode("utf8")
        # delete \n
        output = output.rstrip('\n')
        node_list_reverse = output.split()
        node_list = list(reversed(node_list_reverse))

        file_output = name + "," + str(cycle) + ","
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
        f.write("name,cycle,node_list,ocu_time,deadline\n")

if __name__ == "__main__":
    data = read_yaml('../flow/flow_hard.yml')
    csv_filename = 'flow_with_path.csv'
    gen_csv_from_data(data, csv_filename)