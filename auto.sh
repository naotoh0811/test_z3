if test -e "result.txt"; then
    rm result.txt
fi

#zg 2vec_sch.cpp
./2vec_sch.out >> result.txt
python3 dataget.py