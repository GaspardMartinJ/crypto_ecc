import random

# Courbe: y² = x³ + ax + b (mod p)
a = 35
b = 3
p = 101
P = (2, 9)  # Point de départ


def euclide_etendu(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = euclide_etendu(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y


def inverse_modulaire(a, m):
    if a < 0:
        a = (a % m + m) % m
    g, x, _ = euclide_etendu(a, m)
    if g != 1:
        raise Exception("L'inverse modulaire n'existe pas")
    return x % m


def addition_points(P, R, a, p):
    if P is None:
        return R
    if R is None:
        return P

    Xp, Yp = P
    Xr, Yr = R

    if Xp == Xr and (Yp + Yr) % p == 0:
        return None

    if Xp == Xr and Yp == Yr:
        return doublement_point(P, a, p)

    s = ((Yr - Yp) * inverse_modulaire(Xr - Xp, p)) % p
    Xq = (s**2 - Xp - Xr) % p
    Yq = (s * (Xp - Xq) - Yp) % p

    return (Xq, Yq)


def doublement_point(P, a, p):
    if P is None:
        return None

    Xp, Yp = P

    if Yp == 0:
        return None

    s = ((3 * Xp**2 + a) * inverse_modulaire(2 * Yp, p)) % p
    Xq = (s**2 - 2 * Xp) % p
    Yq = (s * (Xp - Xq) - Yp) % p

    return (Xq, Yq)


def multiplication_scalaire(k, P, a, p):
    binaire = bin(k)[2:]
    resultat = None

    for bit in binaire:
        resultat = doublement_point(resultat, a, p) if resultat is not None else None
        if bit == "1":
            resultat = addition_points(resultat, P, a, p)

    return resultat


if __name__ == "__main__":
    double = doublement_point(P, a, p)
    print(f"Doublement du point P: 2P = {double}")
    point_somme = addition_points(P, double, a, p)
    print(f"Somme des points P + 2P: 3P = {point_somme}")
    k = random.randint(1, p - 1)
    Q = multiplication_scalaire(k, P, a, p)
    print(f"Point de départ P: {P}")
    print(f"Multiplicateur k: {k}")
    print(f"Point final Q: {Q}")
