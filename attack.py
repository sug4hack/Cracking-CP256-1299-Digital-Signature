from sage.all import *
from hashlib import sha256
from fpylll import IntegerMatrix, LLL
import random
import time

# ==== Kurva Cubic Pell ====

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

# ==== Fungsi Hash ====

def sha2_as_integer(message: str) -> int:
    return int(sha256(message.encode()).hexdigest(), 16)

# ==== Serangan 1 : Weak Nonce ====

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

# ==== Kunci Privat dan Publik ====

lam = randint(1, phi)
pub = lam * G

# ==== Dua Pesan Berbeda ====

msg1 = "hello world"
msg2 = "cryptography!"

s1, alphaG1, sigma1, alpha1 = generate_weak_signature(msg1, lam)
s2, alphaG2, sigma2, alpha2 = generate_weak_signature(msg2, lam)

print("s1 =", s1)
print("s2 =", s2)
print("sigma1 =", sigma1)
print("sigma2 =", sigma2)
print("[DEBUG] lambda =", lam)
print("[DEBUG] alpha1 =", alpha1)
print("[DEBUG] alpha2 =", alpha2)

# ==== Bangun Matriks Lattice ====

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

# ==== LLL Reduction ====
start = time.time()
reduced = LLL.reduction(M)


for row in reduced:
    potential_alpha1 = row[0]
    try:
        recovered_lambda = (s1 - potential_alpha1) // sigma1
        recovered_pub = recovered_lambda * G
        if recovered_pub == pub:
            print("\n[✔] Berhasil memulihkan private key λ!")
            print("Recovered λ =", recovered_lambda)
            print("Original  λ =", lam)
            break
    except Exception as e:
        continue
else:
    print("\n[✘] Gagal memulihkan λ")

# ==== Pengukuran waktu berakhir ====
end = time.time()
elapsed = end - start
print(f"\n⏱ Total waktu eksekusi: {elapsed:.4f} detik")

# === Serangan 2: Leaked Nonce ===

def attack_leaked_nonce(s, sigma, alpha):
    """
    Diberikan signature s, hash pesan sigma, dan nonce α yang bocor
    Mengembalikan private key λ
    """
    lam_recovered = (s - alpha) // sigma
    return lam_recovered

# === Simulasi ===

msg = "pesan rahasia"
sigma = sha2_as_integer(msg)
alpha = randint(1, 2**512)  
s = alpha + sigma * lam

# Asumsikan penyerang tahu s, sigma, alpha
lam_recovered = attack_leaked_nonce(s, sigma, alpha)

print("[✔] Serangan Leaked Nonce berhasil!")
print("Recovered λ:", lam_recovered)
print("Original  λ:", lam)
print("Sama?", lam == lam_recovered)

# === Serangan 3: Reused Nonce ===

def attack_reused_nonce(s1, s2, sigma1, sigma2):
    """
    Menerima dua signature s1, s2 dan hash pesan sigma1, sigma2
    Mengembalikan private key λ jika nonce α diulang
    """
    delta_sigma = sigma1 - sigma2
    if delta_sigma == 0:
        raise ValueError("sigma1 == sigma2, tidak dapat melanjutkan.")
    lam_recovered = (s1 - s2) // delta_sigma
    return lam_recovered

# === Simulasi ===

msg1 = "pesan A"
msg2 = "pesan B"
sigma1 = sha2_as_integer(msg1)
sigma2 = sha2_as_integer(msg2)

# Gunakan nonce α yang sama
alpha = randint(1, 2**512)
s1 = alpha + sigma1 * lam
s2 = alpha + sigma2 * lam

# Pulihkan λ
lam_recovered = attack_reused_nonce(s1, s2, sigma1, sigma2)

print("[✔] Serangan Reuse Nonce berhasil!")
print("Recovered λ:", lam_recovered)
print("Original  λ:", lam)
print("Sama?", lam == lam_recovered)

# ==== Serangan 4: Multi-Key with Shared Nonces ====

def recover_keys_modular(h1, h2, h3, h4, s1, s2, s3, s4, phi):
    """
    Pecahkan sistem linear modular dari dua persamaan untuk recover x1 dan x2
    """
    A = Matrix(Zmod(phi), [[h1, -h2], [h3, -h4]])
    b = vector(Zmod(phi), [s1 - s2, s3 - s4])

    # Coba selesaikan
    try:
        sol = A.solve_right(b)
        return int(sol[0]), int(sol[1])
    except:
        print("Tidak dapat memecahkan sistem. Mungkin determinan tidak invertible.")
        return None, None

# ==== Simulasi ====

# Dua private key berbeda
x1 = randint(1, phi)
x2 = randint(1, phi)

# Dua nonce yang dibagikan
alpha1 = randint(1, 2**512)
alpha2 = randint(1, 2**512)

# Empat pesan
m1 = "pesan1"
m2 = "pesan2"
m3 = "pesan3"
m4 = "pesan4"

h1 = sha2_as_integer(m1)
h2 = sha2_as_integer(m2)
h3 = sha2_as_integer(m3)
h4 = sha2_as_integer(m4)

# Empat tanda tangan
s1 = alpha1 + h1 * x1
s2 = alpha1 + h2 * x2
s3 = alpha2 + h3 * x1
s4 = alpha2 + h4 * x2

# Recovery
x1_rec, x2_rec = recover_keys_modular(h1, h2, h3, h4, s1, s2, s3, s4, phi)

print("\n[✔] Serangan Shared Nonces Modular berhasil!")
print("Recovered x1:", x1_rec)
print("Recovered x2:", x2_rec)
print("Original  x1:", x1)
print("Original  x2:", x2)
print("x1 benar?", x1 == x1_rec)
print("x2 benar?", x2 == x2_rec)

