import re
import time
import subprocess
from collections import Counter



# sudo iptables -F INPUT pour  debloquer toutes les ip d'un coup
# sudo iptables -D INPUT -s (adresse IP) -j DROP pour debloquer une adresse ip



SEUIL = 3
LOG = "/var/log/auth.log"
BLANCHE = {"::1", "127.0.0.1"}          # IP Ã  ne JAMAIS bloquer (soi-mÃªme)
MODE_TEST = False                        # True = on affiche seulement, on ne bloque pas

motif = re.compile(r"from (\S+) port")
compteur = Counter()
deja_traitees = set()


def bloquer(ip):
    """Ajoute une rÃ¨gle iptables pour jeter tout le trafic venant de cette IP."""
    commande = ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]

    if MODE_TEST:
        print(f"   [TEST] commande qui serait lancÃ©e : {' '.join(commande)}")
    else:
        subprocess.run(commande)        # exÃ©cute rÃ©ellement la commande
        print(f"   [BLOQUÃ‰] {ip} via iptables")


with open(LOG, "r") as f:
    f.seek(0, 2)
    print("Surveillance en cours... (Ctrl+C pour arrÃªter)")

    while True:
        ligne = f.readline()
        if not ligne:
            time.sleep(0.5)
            continue

        if "Failed password" in ligne:
            resultat = motif.search(ligne)
            if resultat:
                ip = resultat.group(1)
                compteur[ip] += 1

                if compteur[ip] >= SEUIL and ip not in deja_traitees:
                    print(f"[ALERTE] {ip} a atteint {compteur[ip]} Ã©checs !")
                    deja_traitees.add(ip)

                    if ip in BLANCHE:
                        print(f"   [IGNORÃ‰] {ip} est en liste blanche, pas de blocage.")
                    else:
                        bloquer(ip)
