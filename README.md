## Prerequis

- Python 3.8+
- Dependance Python: `cryptography`

Installation:

```
pip install cryptography
```

## Utilisation

Aide:

```
python ecc_cli.py help
```

Generer une paire de cles (fichiers `monECC.priv` et `monECC.pub`):

```
python ecc_cli.py keygen
```

Generer une paire de cles avec un nom personnalise:

```
python ecc_cli.py keygen -f maCle
```

Chiffrer un message avec une cle publique:

```
python ecc_cli.py crypt maCle.pub "Bonjour le monde"
```

Dechiffrer un message avec une cle privee:

```
python ecc_cli.py decrypt maCle.priv "<texte_chiffre_base64>"
```
