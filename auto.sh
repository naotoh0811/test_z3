if test -e "result.txt"; then
    rm result.txt
fi

CPP="2vec_sch.cpp"
NAME=${CPP%.*}

g++ -D_MP_INTERNAL -DNDEBUG -D_EXTERNAL_RELEASE -D_AMD64_ -D_USE_THREAD_LOCAL  -std=c++11 -fvisibility=hidden -c -mfpmath=sse -msse -msse2 -fopenmp -O3 -D_LINUX_ -fPIC -D_LINUX_  -o _$NAME.o  -I~/workspace/z3/src/api -I~/workspace/z3/src/api/c++ $CPP
g++ -o $NAME.out _$NAME.o ~/workspace/z3/build/libz3.so -lpthread  -fopenmp -lrt
rm _$NAME.o

./2vec_sch.out >> result.txt
python3 dataget.py

