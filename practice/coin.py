# http://bach.istc.kobe-u.ac.jp/papers/pdf/jevec2016.pdf
from z3 import *

x = Int('x')
y = Int('y')
z = Int('z')

a = Int('a')
b = Int('b')

s = Solver()
s.add(x + y + z == 15, x >= 1, y >= 1, z >= 1, x <= 15, y <= 15, z <= 15, x + 5 * y + 10 * z == 90)
#s.add(a % 10 == 1)
#s.add(10 % b == 1)
s.add(b % a == 10)
s.add(a > 20)
s.add(b > 20)


print(s.check())
print(s.model())
