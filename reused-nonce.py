from hashlib import sha256
from fpylll import IntegerMatrix, LLL
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

def attack_reused_nonce(s1, s2, sigma1, sigma2):
    delta_sigma = sigma1 - sigma2
    if delta_sigma == 0:
        raise ValueError("sigma1 == sigma2.")
    lam_recovered = (s1 - s2) // delta_sigma
    return lam_recovered

msg1 = "message A"
msg2 = "message B"
sigma1 = sha2_as_integer(msg1)
sigma2 = sha2_as_integer(msg2)

alpha = randint(1, 2**512)
s1 = alpha + sigma1 * lam
s2 = alpha + sigma2 * lam

lam_recovered = attack_reused_nonce(s1, s2, sigma1, sigma2)

print("[✔] Successs!")
print("Recovered λ:", lam_recovered)
print("Original  λ:", lam)
print("Same?", lam == lam_recovered)
