"""
scrape_tenygasy.py
==================
Collecte de vocabulaire malagasy depuis tenymalagasy.org.

Le site propose un index alphabétique de mots avec définitions.
Le script parcourt chaque page de l'index et extrait les entrées.

Sortie :
  data/corpus/dictionary.json  ← mots filtrés (fusionnés via _filter)

Usage :
  py scripts/scrape_tenygasy.py
"""

import time

import requests
import urllib3
from bs4 import BeautifulSoup
from _filter import is_valid_malagasy, save_dict

# Désactive les alertes SSL (certificat expiré sur tenymalagasy.org)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}
INDEX_URL = "https://tenymalagasy.org/bins/alphaLists"


def get_all_list_links() -> list:
    links = []
    try:
        r = requests.get(INDEX_URL, headers=HEADERS, verify=False, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "alphaLists" in href and href != "alphaLists":
                full = f"https://tenymalagasy.org{href}"
                if full not in links:
                    links.append(full)
    except Exception as e:
        print(f"Erreur index : {e}")
    return links


def scrape_words_from_link(url: str) -> set:
    words = set()
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        for b in soup.find_all("b"):
            w = b.text.strip()
            if is_valid_malagasy(w):
                words.add(w.lower())
    except Exception as e:
        print(f"  Erreur {url}: {e}")
    return words


def main():
    print("=== tenymalagasy.org ===\n")
    print("1. Récupération de l'index alphabétique...")
    all_links = get_all_list_links()
    print(f"   Pages trouvées : {len(all_links)}")

    all_words: set = set()
    for i, link in enumerate(all_links):
        new = scrape_words_from_link(link)
        all_words.update(new)
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(all_links)}] {len(all_words)} mots")
        time.sleep(0.5)

    print(f"\nTotal extrait : {len(all_words)} mots")
    save_dict(all_words, "tenymalagasy")


if __name__ == "__main__":
    main()