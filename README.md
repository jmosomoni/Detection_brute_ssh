# Détecteur de force brute SSH

Script Python qui surveille en temps réel le journal d'authentification Linux,
détecte les attaques par force brute SSH (tentatives de connexion répétées), et
**bloque automatiquement** les adresses IP attaquantes via `iptables`.

Projet d'apprentissage en cybersécurité défensive.

---

## Objectif

Reproduire le comportement d'un outil anti-brute-force (type *fail2ban*, en
version minimaliste et pédagogique) : lire les logs, compter les échecs par IP,
et réagir au-delà d'un seuil.

## Fonctionnement

```
/var/log/auth.log ──► lecture en temps réel ──► compte les échecs par IP
                                                         │
                                          si une IP dépasse le SEUIL
                                                         │
                                          iptables DROP  ◄── (sauf liste blanche)
```

1. Le script se place à la **fin** du journal (`seek`) et lit les **nouvelles** lignes.
2. Pour chaque ligne contenant `Failed password`, il extrait l'IP source (regex).
3. Il compte les échecs par IP avec un `Counter`.
4. Dès qu'une IP atteint le **seuil**, elle est **bloquée** via `iptables`
   (sauf si elle est en **liste blanche**, ex. `127.0.0.1`).

## Technologies

- **Python 3** — `re` (regex), `collections.Counter`, `subprocess`, lecture de log en flux
- **iptables** — pare-feu Linux pour le blocage
- **Linux** — journal `/var/log/auth.log`

## Utilisation

```bash
# Nécessite les droits root (lecture du log + iptables)
sudo python3 detect_bruteforce_ssh.py
```

Paramètres (en haut du script) :

```python
SEUIL = 3                         # nombre d'échecs avant blocage
LOG = "/var/log/auth.log"         # journal à surveiller
BLANCHE = {"::1", "127.0.0.1"}    # IP à ne jamais bloquer
MODE_TEST = False                 # True = simulation (affiche sans bloquer)
```

Mets `MODE_TEST = True` pour tester sans réellement bloquer : le script
affiche la commande `iptables` qu'il **aurait** lancée.

## Débloquer une IP

```bash
# Débloquer une IP précise
sudo iptables -D INPUT -s <adresse_ip> -j DROP

# Débloquer toutes les IP d'un coup
sudo iptables -F INPUT
```

## Tester l'outil

Générer des échecs de connexion SSH (sur une machine de test) :

```bash
# Depuis la même machine, plusieurs tentatives avec un faux utilisateur
for i in $(seq 1 5); do ssh pirate@localhost; done
```

Au-delà du seuil, l'IP est détectée et bloquée (ou affichée en `MODE_TEST`).

## Améliorations possibles

- Débloquer automatiquement une IP après un délai (bannissement temporaire)
- Envoyer une alerte par e-mail à chaque blocage
- Journaliser les blocages dans un fichier avec horodatage
- Gérer la rotation du fichier de log
