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
