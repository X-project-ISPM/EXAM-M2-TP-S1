"""
scrape_bible.py
===============
Extrait le vocabulaire malagasy depuis le corpus Bible (bible_mg.txt).

Le fichier bible_mg.txt contient déjà le texte brut de la Bible en malagasy.
Ce script tokenise le texte et extrait les mots valides.

Sortie :
  data/corpus/dictionary.json  ← mots filtrés (fusionnés via _filter)

Usage :
  py scripts/scrape_bible.py
"""

import re
from _filter import is_valid_malagasy, save_dict, ROOT

BIBLE_PATH = ROOT / "data" / "corpus" / "bible_mg.txt"


def main():
    print("=== Bible Malagasy ===\n")

    if not BIBLE_PATH.exists():
        print(f"Fichier introuvable : {BIBLE_PATH}")
        return

    text = BIBLE_PATH.read_text(encoding="utf-8")
    print(f"Taille du corpus : {len(text):,} caractères")

    tokens = re.findall(r"\b[a-zA-ZôÔâÂîÎ]+\b", text)
    print(f"Tokens bruts     : {len(tokens):,}")

    words = set()
    for t in tokens:
        if is_valid_malagasy(t):
            words.add(t.lower())

    print(f"Mots valides     : {len(words):,}")
    save_dict(words, "bible")


if __name__ == "__main__":
    main()
