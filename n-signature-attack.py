from sage.all import *
from hashlib import sha256
from fpylll import IntegerMatrix, LLL

# ==== Kurva CP256-1299 ==== #
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

# ==== Setup Kurva dan Titik Dasar ==== #
p = 2**256 - 1299
phi = p**2 + p + 1
a = 7
curve = CubicPellCurve(p, a)
G = (p+1) * curve.point(4, 2, 1)

# ==== Fungsi Hash dan Signature ==== #
def sha2_int(msg):
    return int(sha256(msg.encode()).hexdigest(), 16)

def sign(msg, lam, bits_nonce=128):
    sigma = sha2_int(msg)
    alpha = randint(1, 2**bits_nonce)
    s = alpha + sigma * lam
    return (s, sigma, alpha)

# ==== Fungsi Serangan untuk n Signature ==== #
def attack_lattice(s_list, sigma_list, pub, G, phi, B):
    n = len(s_list)
    M = IntegerMatrix(n + 2, n + 2)

    for i in range(n):
        M[i, i] = phi

    for i in range(n):
        M[n, i] = sigma_list[i]
    M[n, n] = B // phi

    for i in range(n):
        M[n+1, i] = s_list[i]
    M[n+1, n+1] = B

    reduced = LLL.reduction(M)

    for row in reduced:
        alpha_guess = row[0]
        try:
            lam_recovered = (s_list[0] - alpha_guess) // sigma_list[0]
            if lam_recovered * G == pub:
                return True
        except:
            continue
    return False

entropy_targets = [128, 160, 192, 224, 256, 257, 258, 259, 260, 264, 272, 280]
trial_count = 10
max_signature_limit = 50

print(f"{'Nonce Bits':>10} | {'Signatures':>10} | {'Success Rate (%)':>17}")
print("-" * 45)

final_results = {}

for bits_nonce in entropy_targets:
    final_results[bits_nonce] = []
    for sig_count in range(2, max_signature_limit + 1):
        success = 0
        for t in range(trial_count):
            lam = randint(1, phi)
            pub = lam * G
            s_list, sigma_list = [], []
            for i in range(sig_count):
                msg = f"msg-{t}-{i}"
                s, sigma, _ = sign(msg, lam, bits_nonce=bits_nonce)
                s_list.append(s)
                sigma_list.append(sigma)

            B = 2**bits_nonce
            if attack_lattice(s_list, sigma_list, pub, G, phi, B):
                success += 1

        rate = round((success / trial_count) * 100, 1)
        final_results[bits_nonce].append((sig_count, rate))
        print(f"{bits_nonce:>10} | {sig_count:>10} | {rate:>17.1f}")

        if bits_nonce > 256:
            if rate >= 70.0:
                break
        else:
            if rate == 100.0 or rate == 90.0:
                break
