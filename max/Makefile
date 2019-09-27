main.o: inter.o
ifeq ($(shell uname), Darwin)
	g++ -o main.o inter.o ~/workspace/z3/build/libz3.dylib -lpthread
else
ifeq ($(shell uname), Linux)
	g++ -o main.o inter.o /share/home/hagino/workspace/z3/build/libz3.so -lpthread  -fopenmp -lrt
endif
endif
	rm inter.o

inter.o: max_test.cpp
ifeq ($(shell uname), Darwin)
	g++ -D_MP_INTERNAL -DNDEBUG -D_EXTERNAL_RELEASE  -std=c++11 -fvisibility=hidden -c -mfpmath=sse -msse -msse2 -D_NO_OMP_ -O3 -Wno-unknown-pragmas -Wno-overloaded-virtual -Wno-unused-value -fPIC -o inter.o -I~/workspace/z3/src/api -I~/workspace/z3/src/api/c++ max_test.cpp
else
ifeq ($(shell uname), Linux)
	g++ -D_MP_INTERNAL -DNDEBUG -D_EXTERNAL_RELEASE -D_AMD64_ -D_USE_THREAD_LOCAL  -std=c++11 -fvisibility=hidden -c -mfpmath=sse -msse -msse2 -fopenmp -O3 -D_LINUX_ -fPIC -D_LINUX_ -o inter.o -I/share/home/hagino/workspace/z3/src/api -I/share/home/hagino/workspace/z3/src/api/c++ max_test.cpp
endif
endif
