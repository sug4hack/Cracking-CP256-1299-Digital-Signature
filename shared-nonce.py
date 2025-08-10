from hashlib import sha256
from fpylll import IntegerMatrix, LLL
import random
import time

class CubicPellCurve:
    def __init__(self, N, a):
        self.N = N
        self.ZN = Zmod(N)
        self.a = self.ZN(a)
    
    def point(self, x, y, z):
        return CubicPellPoint(self, self.ZN(x), self.ZN(y), self.ZN(z))

    def zero(self):
        return CubicPellPoint(self, self.ZN(1), self.ZN(0), self.ZN(0))

class CubicPellPoint:
    def __init__(self, curve, x, y, z):
        self.curve = curve
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, Q):
        a = self.curve.a
        x1, y1, z1 = self.x, self.y, self.z
        x2, y2, z2 = Q.x, Q.y, Q.z

        x3 = x1 * x2 + a * (y2 * z1 + y1 * z2)
        y3 = x2 * y1 + x1 * y2 + a * z1 * z2
        z3 = y1 * y2 + x2 * z1 + x1 * z2

        return CubicPellPoint(self.curve, x3, y3, z3)

    def __rmul__(self, n):
        R = self.curve.zero()
        Q = self
        for bit in bin(n)[2:]:
            R = R + R
            if bit == '1':
                R = R + Q
        return R

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __repr__(self):
        return f"({self.x} : {self.y} : {self.z})"
        

def recover_keys_modular(h1, h2, h3, h4, s1, s2, s3, s4, phi):
    A = Matrix(Zmod(phi), [[h1, -h2], [h3, -h4]])
    b = vector(Zmod(phi), [s1 - s2, s3 - s4])

    try:
        sol = A.solve_right(b)
        return int(sol[0]), int(sol[1])
    except:
        print("not invertible.")
        return None, None


x1 = randint(1, phi)
x2 = randint(1, phi)

alpha1 = randint(1, 2**512)
alpha2 = randint(1, 2**512)

m1 = "message1"
m2 = "message2"
m3 = "message3"
m4 = "message4"

h1 = sha2_as_integer(m1)
h2 = sha2_as_integer(m2)
h3 = sha2_as_integer(m3)
h4 = sha2_as_integer(m4)

s1 = alpha1 + h1 * x1
s2 = alpha1 + h2 * x2
s3 = alpha2 + h3 * x1
s4 = alpha2 + h4 * x2

x1_rec, x2_rec = recover_keys_modular(h1, h2, h3, h4, s1, s2, s3, s4, phi)

print("\n[✔] Success")
print("Recovered x1:", x1_rec)
print("Recovered x2:", x2_rec)
print("Original  x1:", x1)
print("Original  x2:", x2)
print("x1 true?", x1 == x1_rec)
print("x2 true?", x2 == x2_rec)
