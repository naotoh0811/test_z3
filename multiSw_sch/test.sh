for i in `seq 10`
do
    echo $i
    python3 gen_network_and_flow.py 15 15 14
    python3 sch_with_soft.py False
    python3 sch_with_soft.py True
done