"""
build_dictionary.py
====================
Nettoie et valide le dictionnaire malagasy unifié.

Source unique :
  data/corpus/dictionary.json     ← tous les scrapers écrivent ici

Sortie :
  data/corpus/dictionary.json     ← nettoyé sur place
  backend/data/corpus/dictionary.json ← copie pour le backend

Règles de nettoyage :
  - Longueur >= 3 caractères, uniquement alphabétique (malagasy + ôâî)
  - Pas de bruit répétitif (aaa…), pas de doubles consonnes initiales (dd…)
  - Pas de mots français/anglais/web dans la liste d'exclusion
  - Phonotaxie malagasy : nb, mk, nk, dt, bp, sz → rejeté
  - Pas d'inflexions de noms étrangers (explosion Wikipedia MG)
  - Pas de clusters de 4+ consonnes consécutives

Usage :
  python scripts/build_dictionary.py
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DICT = ROOT / "data" / "corpus" / "dictionary.json"   # source unique

# ---------------------------------------------------------------------------
# Filtres
# ---------------------------------------------------------------------------

EXCLUDED = {
    # Français
    "de", "du", "au", "le", "la", "les", "un", "une", "des", "en",
    "et", "ou", "par", "pour", "sur", "dans", "avec", "qui", "que",
    "il", "elle", "ils", "elles", "vous", "nous", "je", "tu",
    "communaute", "communes", "departement", "commune",
    "france", "paris", "lyon", "marseille",
    # Néerlandais / allemand
    "von", "van", "der", "den", "het",
    # Anglais
    "the", "be", "by", "new", "york", "ridge", "and", "for",
    # Fragments web / codes bibliographiques
    "archived", "com", "epub", "img", "imgp", "org", "wayback", "jwpub",
    "isbn", "issn", "doi", "freebase", "insee", "http", "https",
    "at", "od",
}

VALID_CHARS        = re.compile(r'^[a-zôâî]+$')
FORBIDDEN_PHONOTAX = re.compile(r'nb|mk|nk|dt|bp|sz')
FOREIGN_INFLECTION = re.compile(
    r'(anao|anareo|anay|ianiko|ianina|ianinao|ianinareo|ianinery|ianiny|'
    r'inanay|ananareo|iniko|inina|ininao|inareo|inary|ininy)$'
)
CONSONANT_CLUSTER  = re.compile(r'[bcdfgjklmnpqrstvwxyz]{4,}')


def _is_noise(w: str) -> bool:
    if len(set(w)) == 1 and len(w) > 2:            # "aaa", "eeee"
        return True
    if len(w) >= 4 and w[0] == w[1] and w[0] not in "aeiou":  # "ddrakizay"
        return True
    return False


def is_valid(word: str) -> bool:
    w = word.lower().strip()
    if len(w) < 3:                         return False
    if not VALID_CHARS.match(w):           return False
    if _is_noise(w):                       return False
    if w in EXCLUDED:                      return False
    if FORBIDDEN_PHONOTAX.search(w):       return False
    if FOREIGN_INFLECTION.search(w):       return False
    if CONSONANT_CLUSTER.search(w):        return False
    return True

# ---------------------------------------------------------------------------
# Script principal
# ---------------------------------------------------------------------------

def build():
    if not DICT.exists():
        print(f"DICT introuvable : {DICT}")
        return

    with open(DICT, "r", encoding="utf-8") as f:
        raw = json.load(f)

    print(f"Entrées brutes     : {len(raw)}")

    cleaned: list[str] = sorted({w.lower().strip() for w in raw if isinstance(w, str) and is_valid(w)})

    print(f"Après nettoyage    : {len(cleaned)} conservées")
    print(f"Rejetées           : {len(raw) - len(cleaned)}")

    # Écriture en place
    with open(DICT, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print(f"✓ Mis à jour       : {DICT.relative_to(ROOT)}")

    # Invalide le cache n-gram
    for cache in ROOT.rglob("ngram_model.pkl"):
        cache.unlink()
        print(f"✓ Cache supprimé   : {cache.relative_to(ROOT)}")
    ngram_cache = ROOT / "data" / "corpus" / "ngram_model.pkl"
    if ngram_cache.exists():
        ngram_cache.unlink()
        print(f"✓ Cache supprimé   : {ngram_cache.relative_to(ROOT)}")

    print(f"\nDictionnaire final : {len(cleaned)} mots malagasy")


if __name__ == "__main__":
    build()
