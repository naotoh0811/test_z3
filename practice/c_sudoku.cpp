#include"z3++.h"

using namespace z3;


void sudoku_example() {
    std::cout << "sudoku example\n";

    context c;

    // 9x9 matrix of integer variables 
    expr_vector x(c);
    for (unsigned i = 0; i < 9; ++i)
        for (unsigned j = 0; j < 9; ++j) {
            std::stringstream x_name;

            x_name << "x_" << i << '_' << j;
            x.push_back(c.int_const(x_name.str().c_str()));
        }

    solver s(c);

    // each cell contains a value in {1, ..., 9}
    for (unsigned i = 0; i < 9; ++i)
        for (unsigned j = 0; j < 9; ++j) {
            s.add(x[i * 9 + j] >= 1 && x[i * 9 + j] <= 9);
        }

    // each row contains a digit at most once
    for (unsigned i = 0; i < 9; ++i) {
        expr_vector t(c);
        for (unsigned j = 0; j < 9; ++j)
            t.push_back(x[i * 9 + j]);
        s.add(distinct(t));
    }

    // each column contains a digit at most once
    for (unsigned j = 0; j < 9; ++j) {
        expr_vector t(c);
        for (unsigned i = 0; i < 9; ++i)
            t.push_back(x[i * 9 + j]);
        s.add(distinct(t));
    }

    // each 3x3 square contains a digit at most once
    for (unsigned i0 = 0; i0 < 3; i0++) {
        for (unsigned j0 = 0; j0 < 3; j0++) {
            expr_vector t(c);
            for (unsigned i = 0; i < 3; i++)
                for (unsigned j = 0; j < 3; j++)
                    t.push_back(x[(i0 * 3 + i) * 9 + j0 * 3 + j]);
            s.add(distinct(t));
        }
    }

    // sudoku instance, we use '0' for empty cells
    int instance[9][9] = {{0,0,0,0,9,4,0,3,0},
                          {0,0,0,5,1,0,0,0,7},
                          {0,8,9,0,0,0,0,4,0},
                          {0,0,0,0,0,0,2,0,8},
                          {0,6,0,2,0,1,0,5,0},
                          {1,0,2,0,0,0,0,0,0},
                          {0,7,0,0,0,0,5,2,0},
                          {9,0,0,0,6,5,0,0,0},
                          {0,4,0,9,7,0,0,0,0}};

    for (unsigned i = 0; i < 9; i++)
        for (unsigned j = 0; j < 9; j++)
            if (instance[i][j] != 0)
                s.add(x[i * 9 + j] == instance[i][j]);

    std::cout << s.check() << std::endl;
    std::cout << s << std::endl;

    model m = s.get_model();
    for (unsigned i = 0; i < 9; ++i) {
        for (unsigned j = 0; j < 9; ++j)
            std::cout << m.eval(x[i * 9 + j]);
        std::cout << '\n';
    }
}


int main(int argc, char *argv[]) {
	int arg = 10;
	if (argc > 1) arg = atoi(argv[1]);
    try {
        sudoku_example();
		std::cout << "\n";
        std::cout << "done\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }
    return 0;
}
