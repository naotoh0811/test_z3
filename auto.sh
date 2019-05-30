CPP="2vec_sch.cpp"
NAME=${CPP%.*}

if [ "$(uname)" == 'Darwin' ]; then
    g++ -D_MP_INTERNAL -DNDEBUG -D_EXTERNAL_RELEASE  -std=c++11 -fvisibility=hidden -c -mfpmath=sse -msse -msse2 -D_NO_OMP_ -O3 -Wno-unknown-pragmas -Wno-overloaded-virtual -Wno-unused-value -fPIC   -o _$NAME.o  -I~/workspace/z3/src/api -I~/workspace/z3/src/api/c++ $CPP
    g++ -o $NAME.out _$NAME.o  ~/workspace/z3/build/libz3.dylib -lpthread
else
    g++ -D_MP_INTERNAL -DNDEBUG -D_EXTERNAL_RELEASE -D_AMD64_ -D_USE_THREAD_LOCAL  -std=c++11 -fvisibility=hidden -c -mfpmath=sse -msse -msse2 -fopenmp -O3 -D_LINUX_ -fPIC -D_LINUX_  -o _$NAME.o  -I~/workspace/z3/src/api -I~/workspace/z3/src/api/c++ $CPP
    g++ -o $NAME.out _$NAME.o ~/workspace/z3/build/libz3.so -lpthread  -fopenmp -lrt
fi

rm _$NAME.o
./$NAME.out
python3 dataget.py