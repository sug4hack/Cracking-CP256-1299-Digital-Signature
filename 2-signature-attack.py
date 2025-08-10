from sage.all import *
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

def sha2_as_integer(message: str) -> int:
    return int(sha256(message.encode()).hexdigest(), 16)

p = 2**256 - 1299
phi = p**2 + p + 1
a = 7
curve = CubicPellCurve(p, a)

G = curve.point(4, 2, 1)
G = (p+1) * G 

def generate_weak_signature(msg, lam):
    sigma = sha2_as_integer(msg)
    alpha = random.randint(1, 2**256) 
    s = alpha + sigma * lam
    alphaG = alpha * G
    return (s, alphaG, sigma, alpha)

lam = randint(1, phi)
pub = lam * G

msg1 = "hello world"
msg2 = "cryptography!"

s1, alphaG1, sigma1, alpha1 = generate_weak_signature(msg1, lam)
s2, alphaG2, sigma2, alpha2 = generate_weak_signature(msg2, lam)

print("s1 =", s1)
print("s2 =", s2)
print("sigma1 =", sigma1)
print("sigma2 =", sigma2)
print("lambda =", lam)
print("alpha1 =", alpha1)
print("alpha2 =", alpha2)

B = 2**256

M = IntegerMatrix(4, 4)
M[0, 0] = phi
M[1, 1] = phi
M[2, 0] = int(sigma1)
M[2, 1] = int(sigma2)
M[2, 2] = int(B // phi)
M[3, 0] = int(s1)
M[3, 1] = int(s2)
M[3, 3] = int(B)

start = time.time()
reduced = LLL.reduction(M)

for row in reduced:
    potential_alpha1 = row[0]
    try:
        recovered_lambda = (s1 - potential_alpha1) // sigma1
        recovered_pub = recovered_lambda * G
        if recovered_pub == pub:
            print("\n[✔] Success!")
            print("Recovered λ =", recovered_lambda)
            print("Original  λ =", lam)
            break
    except Exception as e:
        continue
else:
    print("\n[✘] Failed")

end = time.time()
elapsed = end - start
print(f"\n⏱ Total time: {elapsed:.4f} s")
