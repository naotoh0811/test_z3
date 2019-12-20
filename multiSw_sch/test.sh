function repeat_gen_and_sch(){
    for i in `seq 10`
    do
        echo $i
        python3 gen_network_and_flow.py 5 5 4
        python3 sch_with_soft.py False
        python3 sch_with_soft.py True
    done
}

repeat_gen_and_sch