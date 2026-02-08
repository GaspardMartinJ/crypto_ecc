from ecc import a, p, P, multiplication_scalaire
import random
import sys
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def afficher_aide():
    print(
        """
Script monECC par Gaspard
Syntaxe :
    monECC <commande> [<clé>] [<texte>] [switchs]
Commande :
    keygen : Génère une paire de clé
    crytp : Chiffre <texte> pour la clé publique <clé>
    decrytp: Déchiffre <texte> pour la clé privée <clé>
    help : Affiche ce manuel
Clé :
    Un fichier qui contient une clé publique monECC ("crypt") ou une clé privée ("decrypt")
Texte :
    Une phrase en clair ("crypt") ou une phrase chiffrée ("decrypt")
Switchs :
    -f <file> permet de choisir le nom des clé générés, monECC.pub et monECC.priv par défaut
"""
    )


def keygen(nom_fichier="monECC"):
    Q = None
    while Q is None:
        k = random.randint(1, p - 1)
        Q = multiplication_scalaire(k, P, a, p)

    fichier_priv = f"{nom_fichier}.priv"
    with open(fichier_priv, "w") as f:
        f.write("---begin monECC private key---\n")
        k_base64 = base64.b64encode(str(k).encode()).decode()
        f.write(f"{k_base64}\n")
        f.write("---end monECC key---\n")

    fichier_pub = f"{nom_fichier}.pub"
    with open(fichier_pub, "w") as f:
        f.write("---begin monECC public key---\n")
        q_string = f"{Q[0]};{Q[1]}"
        q_base64 = base64.b64encode(q_string.encode()).decode()
        f.write(f"{q_base64}\n")
        f.write("---end monECC key---\n")

    print("Génération de clés terminée")
    return fichier_priv, fichier_pub


def lire_cle_publique(fichier):
    try:
        with open(fichier, "r") as f:
            lignes = f.readlines()

        if not lignes[0].strip() == "---begin monECC public key---":
            print(f"Erreur: {fichier} n'est pas une clé publique valide")
            return None

        q_base64 = lignes[1].strip()
        q_string = base64.b64decode(q_base64).decode()
        qx, qy = q_string.split(";")
        Q = (int(qx), int(qy))

        return Q

    except Exception as e:
        print(f"Erreur lors de la lecture de la clé: {e}")
        return None


def lire_cle_privee(fichier):
    try:
        with open(fichier, "r") as f:
            lignes = f.readlines()

        if not lignes[0].strip() == "---begin monECC private key---":
            print(f"Erreur: {fichier} n'est pas une clé privée valide")
            return None

        k_base64 = lignes[1].strip()
        k = int(base64.b64decode(k_base64).decode())

        print(f"Clé privée chargée: k = {k}")
        return k

    except Exception as e:
        print(f"Erreur lors de la lecture de la clé: {e}")
        return None


def crypt(fichier_cle_pub, texte_clair):
    Qb = lire_cle_publique(fichier_cle_pub)
    if Qb is None:
        return None

    S = None
    while S is None:
        ka = random.randint(1, p - 1)
        Qa = multiplication_scalaire(ka, P, a, p)
        if Qa is not None:
            S = multiplication_scalaire(ka, Qb, a, p)

    secret_bytes = str(S[0]).encode() + str(S[1]).encode()
    secret_hash = hashlib.sha256(secret_bytes).digest()

    iv = secret_hash[:16]
    cle = secret_hash[16:]

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(texte_clair.encode("utf-8"))
    padded_data += padder.finalize()

    cipher = Cipher(algorithms.AES(cle), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    resultat = f"{Qa[0]};{Qa[1]}:{ciphertext.hex()}"
    resultat_base64 = base64.b64encode(resultat.encode()).decode()

    print("Message chiffré avec succès!")
    return resultat_base64


def decrypt(fichier_cle_priv, texte_chiffre):
    kb = lire_cle_privee(fichier_cle_priv)
    if kb is None:
        return None

    try:
        resultat = base64.b64decode(texte_chiffre).decode()
        parties = resultat.split(":")
        qa_coords = parties[0].split(";")
        Qa = (int(qa_coords[0]), int(qa_coords[1]))
        ciphertext = bytes.fromhex(parties[1])

        S = multiplication_scalaire(kb, Qa, a, p)

        secret_bytes = str(S[0]).encode() + str(S[1]).encode()
        secret_hash = hashlib.sha256(secret_bytes).digest()

        iv = secret_hash[:16]
        cle = secret_hash[16:]

        cipher = Cipher(algorithms.AES(cle), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded)
        decrypted_data += unpadder.finalize()

        texte_clair = decrypted_data.decode("utf-8")

        print("Message déchiffré avec succès!")
        return texte_clair

    except Exception as e:
        print(f"Erreur lors du déchiffrement: {e}")
        return None


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "help":
        afficher_aide()
        return

    commande = sys.argv[1].lower()

    if commande == "keygen":
        nom_fichier = "monECC"
        if len(sys.argv) > 2 and sys.argv[2] == "-f":
            if len(sys.argv) < 4:
                print("Erreur: Le switch -f nécessite un nom de fichier")
                return
            nom_fichier = sys.argv[3]

        keygen(nom_fichier)

    elif commande == "crypt":
        if len(sys.argv) < 4:
            print("Erreur: La commande 'crypt' nécessite <clé> et <texte>")
            return

        fichier_cle = sys.argv[2]
        texte = sys.argv[3]

        resultat = crypt(fichier_cle, texte)
        if resultat:
            print(f"\n{'='*70}")
            print("TEXTE CHIFFRÉ (base64):")
            print(f"{'='*70}")
            print(resultat)
            print(f"{'='*70}")

    elif commande == "decrypt":
        if len(sys.argv) < 4:
            print("Erreur: La commande 'decrypt' nécessite <clé> et <texte>")
            return

        fichier_cle = sys.argv[2]
        texte_chiffre = sys.argv[3]

        resultat = decrypt(fichier_cle, texte_chiffre)
        if resultat:
            print(f"\n{'='*70}")
            print("TEXTE DÉCHIFFRÉ:")
            print(f"{'='*70}")
            print(resultat)
            print(f"{'='*70}")

    else:
        print(f"Erreur: Commande '{commande}' inconnue")


if __name__ == "__main__":
    main()
