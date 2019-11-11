if [ $# -ne 2 ]; then
    echo "ERROR: invalid args"
    exit 1
fi

NUM_SW=$1
NUM_FLOW=$2

# generate network/network.csv, node.csv
echo Now generating network.csv, node.csv
cd ~/workspace/test_z3/network/network/
python3 gen_linear_network.py $1

# generate flow/flow_hard.yml using network/node.csv
echo Now generating flow_hard.yml
cd ~/workspace/test_z3/network/flow/
python3 gen_flow_using_network_csv.py $2

# generate dijkstra/flow_with_path.csv using network/network.csv, network/node.csv, flow/flow_hard.yml
echo Now generating flow_with_path.csv
cd ~/workspace/test_z3/network/dijkstra/
make
python3 gen_flowData.py

# generate GCLs using dijkstra/flow_with_path.csv
echo Now generating GCLs
echo ------------
cd ~/workspace/test_z3/multiSw_sch
time python3 sch.py
echo ------------

