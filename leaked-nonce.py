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


