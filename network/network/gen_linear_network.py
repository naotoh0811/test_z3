import sys

def gen_network_csv(num_sw, csv_filename):
    output = "nodeFrom,nodeTo,cost\n"
    for i in range(num_sw):
        if i != num_sw - 1:
            output += '{},{},{}\n'.format(i, i+1, 10)
        output += '{},{},{}\n'.format(i, num_sw+i*2, 10)
        output += '{},{},{}\n'.format(i, num_sw+i*2+1, 10)
    with open(csv_filename, 'w') as f:
        f.write(output)

def gen_node_csv(num_sw, csv_filename):
    i_sw_last = num_sw - 1
    i_cli_first = num_sw
    i_cli_last = 3 * num_sw - 1

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

def gen_csv(num_sw, network_csv_filename, node_csv_filename):
    gen_network_csv(num_sw, network_csv_filename)
    gen_node_csv(num_sw, node_csv_filename)


if __name__ == "__main__":
    num_sw = 3
    if len(sys.argv) != 2:
        print("ERROR: arg is invalid")
        exit()
    num_sw = int(sys.argv[1])
    gen_csv(num_sw, 'network.csv', 'node.csv')
