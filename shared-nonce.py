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
