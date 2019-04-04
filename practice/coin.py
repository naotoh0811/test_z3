# http://bach.istc.kobe-u.ac.jp/papers/pdf/jevec2016.pdf
from z3 import *

x = Int('x')
y = Int('y')
z = Int('z')
s = Solver()
s.add(x + y + z == 15, x >= 1, y >= 1, z >= 1, x <= 15, y <= 15, z <= 15, x + 5 * y + 10 * z == 90)
print(s.check())
print(s.model())
