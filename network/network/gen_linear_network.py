import sys
import os.path


def gen_network_csv(num_sw, num_cli_for_each_sw, csv_filename):
    output = "nodeFrom,nodeTo,cost\n"
    for i in range(num_sw):
        cost = 10
        if i != num_sw - 1:
            output += '{},{},{}\n'.format(i, i+1, cost)
        for j in range(num_cli_for_each_sw):
            output += '{},{},{}\n'.format(i, num_sw+num_cli_for_each_sw*i+j, cost)
    with open(csv_filename, 'w') as f:
        f.write(output)

def gen_node_csv(num_sw, num_cli_for_each_sw, csv_filename):
    i_sw_last = num_sw - 1
    i_cli_first = num_sw
    # i_cli_last = 3 * num_sw - 1
    i_cli_last = (num_cli_for_each_sw + 1) * num_sw - 1

    sw_list = list(range(0, i_sw_last+1))
    cli_list = list(range(i_cli_first, i_cli_last+1))

    output = 'sw,cli\n'

    sw_list_output = ""
    for i in sw_list:
        sw_list_output += str(i) + " "
    sw_list_output = sw_list_output.rstrip(' ')
    cli_list_output = ""
    for i in cli_list:
        cli_list_output += str(i) + " "
    cli_list_output = cli_list_output.rstrip(' ')

    output += sw_list_output + "," + cli_list_output + "\n"

    with open(csv_filename, 'w') as f:
        f.write(output)

def gen_csv(num_sw, num_cli_for_each_sw, network_csv_filename, node_csv_filename):
    gen_network_csv(num_sw, num_cli_for_each_sw, network_csv_filename)
    gen_node_csv(num_sw, num_cli_for_each_sw, node_csv_filename)

def main(num_sw, num_cli_for_each_sw):
    home_dir = os.path.expanduser('~')
    gen_csv( \
        num_sw, \
        num_cli_for_each_sw, \
        '{}/workspace/test_z3/network/network/network.csv'.format(home_dir), \
        '{}/workspace/test_z3/network/network/node.csv'.format(home_dir))


if __name__ == "__main__":
    num_sw = 3
    num_cli_for_each_sw = 2
    if len(sys.argv) == 3:
        num_sw = int(sys.argv[1])
        num_cli_for_each_sw = int(sys.argv[2])
    else:
        print("WARNING: arg is invalid. Now set num_sw to 3, num_cli_for_each_sw to 2.")

    main(num_sw, num_cli_for_each_sw)