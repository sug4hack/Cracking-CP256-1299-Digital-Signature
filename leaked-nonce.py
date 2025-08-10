from sage.all import *
from hashlib import sha256
import random

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

def attack_leaked_nonce(s, sigma, alpha):
    lam_recovered = (s - alpha) // sigma
    return lam_recovered

msg = "secret message"
sigma = sha2_as_integer(msg)
alpha = randint(1, 2**512)  
s = alpha + sigma * lam

lam_recovered = attack_leaked_nonce(s, sigma, alpha)

print("[✔] Success!")
print("Recovered λ:", lam_recovered)
print("Original  λ:", lam)
print("Same?", lam == lam_recovered)


