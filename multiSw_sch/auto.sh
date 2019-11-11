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

