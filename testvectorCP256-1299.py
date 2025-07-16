# Tes Vektor ini berdasarkan contoh perhitungan pada https://www.ijcte.org/vol17/IJCTE-V17N2-1371.pdf

from sage.all import *

class CubicPellCurve:
    def __init__(self, N, a):
        self.N = N
        self.ZN = Zmod(N)
        self.a = self.ZN(a)
    
    def __repr__(self):
        return f"CubicPellCurve over Zmod({self.N}) defined by x**3 + {self.a}*y**3 + {self.a**2}*z**3 - 3*{self.a}*x*y*z = 1"

    def is_on_curve(self, P):
        x, y, z = P.x, P.y, P.z
        lhs = x**3 + self.a * y**3 + self.a**2 * z**3 - 3 * self.a * x * y * z
        return lhs == 1

    def zero(self):
        return CubicPellPoint(self, self.ZN(1), self.ZN(0), self.ZN(0))

    def point(self, x, y, z):
        return CubicPellPoint(self, self.ZN(x), self.ZN(y), self.ZN(z))


class CubicPellPoint:
    def __init__(self, curve, x, y, z):
        self.curve = curve
        self.x = x
        self.y = y
        self.z = z
        assert isinstance(curve, CubicPellCurve)

    def __repr__(self):
        return f"({self.x} : {self.y} : {self.z})"

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __neg__(self):
        x, y, z = self.x, self.y, self.z
        a = self.curve.a
        return CubicPellPoint(
            self.curve,
            x**2 - a * y * z,
            a * z**2 - x * y,
            y**2 - x * z
        )

    def __add__(self, Q):
        x1, y1, z1 = self.x, self.y, self.z
        x2, y2, z2 = Q.x, Q.y, Q.z
        a = self.curve.a

        x3 = x1 * x2 + a * (y2 * z1 + y1 * z2)
        y3 = x2 * y1 + x1 * y2 + a * z1 * z2
        z3 = y1 * y2 + x2 * z1 + x1 * z2

        return CubicPellPoint(self.curve, x3, y3, z3)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return NotImplemented

    def __rmul__(self, n):
        if n < 0:
            return (-self).__rmul__(-n)

        R = self.curve.zero()
        Q = self
        for bit in bin(n)[2:]:
            R = R + R
            if bit == '1':
                R = R + Q
        return R


from hashlib import sha256

# Parameter sistem
p = 2**256 - 1299
print("Parameter p:", p)
c = 7  # parameter kurva
print("Parameter c:", c)
curve = CubicPellCurve(p, c)
print(curve)
phi = p**2 + p + 1
print("Nilai phi:", phi)

# Titik dasar (x, y, z) dari tabel pada c = 7
G = curve.point(4, 2, 1)
G = (p+1) * G
print("Titik dasar G:", G)

lam = 83171353578472409519651024131274511974299080148110592010555215815306508292189

pub = lam * G
print("Kunci publik:", pub)

alpha = 1898447103622844920724746489941849722817899851712074472424000756938513692055457989388262477747016063373675722356875332766031268189759451703052827185580311

alphaG = alpha * G
print("Titik alpha * G:", alphaG)

import hashlib

def sha2_as_integer(message: str) -> int:
    # Ubah ke bytes
    msg_bytes = message.encode('utf-8')

    # Hitung SHA-256
    sha_digest = hashlib.sha256(msg_bytes).hexdigest()

    # Konversi hasil hash (hex) ke integer
    hash_integer = int(sha_digest, 16)

    return hash_integer

# Contoh penggunaan
msg = "abc"
sigma = sha2_as_integer(msg)    
print("Nilai sigma:", sigma)

s = alpha + sigma * lam
print("Nilai s:", s)

#signature pair (alphaG, s)
signature = (alphaG, s)
print("Signature pair (alphaG, s):", signature)

#verify
#compute hash of message
sigma = sha2_as_integer(msg)
print("Hash of message:", sigma)

#compute Q=s*G
Q = s * G
print("Computed Q:", Q)

#compute msg_hash * pub
msg_hash_pub = sigma * pub
print("Computed msg_hash * pub:", msg_hash_pub)

#compute Q' = alphaG + sigma*msg_hash_pub
Q_prime = alphaG + msg_hash_pub
print("Computed Q':", Q_prime)

#is Q == Q'?
if Q == Q_prime:
    print("Signature is valid.")
else:
    print("Signature is invalid.")
print("Signature verification complete.")
