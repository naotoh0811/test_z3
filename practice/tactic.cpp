#include"z3++.h"

using namespace z3;


void tactic_example1() {
    /*
      Z3 implements a methodology for orchestrating reasoning engines where "big" symbolic
      reasoning steps are represented as functions known as tactics, and tactics are composed
      using combinators known as tacticals. Tactics process sets of formulas called Goals.

      When a tactic is applied to some goal G, four different outcomes are possible. The tactic succeeds
      in showing G to be satisfiable (i.e., feasible); succeeds in showing G to be unsatisfiable (i.e., infeasible); 
      produces a sequence of subgoals; or fails. When reducing a goal G to a sequence of subgoals G1, ..., Gn, 
      we face the problem of model conversion. A model converter construct a model for G using a model for some subgoal Gi.

      In this example, we create a goal g consisting of three formulas, and a tactic t composed of two built-in tactics: 
      simplify and solve-eqs. The tactic simplify apply transformations equivalent to the ones found in the command simplify. 
      The tactic solver-eqs eliminate variables using Gaussian elimination. Actually, solve-eqs is not restricted 
      only to linear arithmetic. It can also eliminate arbitrary variables. 
      Then, sequential composition combinator & applies simplify to the input goal and solve-eqs to each subgoal produced by simplify. 
      In this example, only one subgoal is produced.
    */
    std::cout << "tactic example 1\n";
    context c;
    expr x = c.real_const("x");
    expr y = c.real_const("y");
    goal g(c);
    g.add(x > 0);
    g.add(y > 0);
    g.add(x == y + 2);
    std::cout << g << "\n";
    tactic t1(c, "simplify");
    tactic t2(c, "solve-eqs");
    tactic t = t1 & t2;
    apply_result r = t(g);
    std::cout << r << "\n";
}


int main(int argc, char *argv[]) {
	int arg = 10;
	if (argc > 1) arg = atoi(argv[1]);
    try {
        tactic_example1();
		std::cout << "\n";
        std::cout << "done\n";
    }
    catch (exception & ex) {
        std::cout << "unexpected error: " << ex << "\n";
    }
    return 0;
}
