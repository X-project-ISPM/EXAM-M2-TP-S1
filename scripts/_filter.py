"""
_filter.py — Utilitaire partagé de filtrage lexical malagasy.
Importé par tous les scrapers. Ne pas exécuter directement.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT = ROOT / "data" / "corpus" / "dictionary.json"

# ---------------------------------------------------------------------------
# Règles phonotactiques du Malagasy
# ---------------------------------------------------------------------------

_VALID_CHARS   = re.compile(r'^[a-zôâî]+$')
_FORBIDDEN     = re.compile(r'nb|mk|nk|dt|bp|sz')
_CONSONANTS    = re.compile(r'[bcdfgjklmnpqrstvwxyz]{4,}')
_NOISE_REPEAT  = re.compile(r'^(.)\1{2,}$')           # aaa, eeee…
_FOREIGN_INFL  = re.compile(
    r'(anao|anareo|anay|ianiko|ianina|ianinao|ianinareo|ianinery|ianiny|'
    r'inanay|ananareo|iniko|inina|ininao|inareo|inary|ininy)$'
)

_EXCLUDED = {
    "de", "du", "au", "le", "la", "les", "un", "une", "des", "en",
    "et", "ou", "par", "pour", "sur", "dans", "avec", "qui", "que",
    "il", "elle", "ils", "elles", "vous", "nous", "je", "tu",
    "von", "van", "der", "den", "het",
    "the", "be", "by", "and", "for", "new", "york", "ridge",
    "archived", "com", "epub", "img", "imgp", "org", "wayback", "jwpub",
    "isbn", "issn", "doi", "freebase", "insee", "http", "https", "at", "od",
    "france", "paris", "lyon", "marseille",
}


def is_valid_malagasy(word: str) -> bool:
    """
    Retourne True si le mot peut être considéré comme du Malagasy valide.
    Utilisé par tous les scrapers pour filtrer en temps réel.
    """
    w = word.lower().strip()
    if len(w) < 3:                        return False
    if not _VALID_CHARS.match(w):         return False
    if _NOISE_REPEAT.match(w):            return False
    if w in _EXCLUDED:                    return False
    if _FORBIDDEN.search(w):              return False
    if _FOREIGN_INFL.search(w):           return False
    if _CONSONANTS.search(w):             return False
    # Au moins 25% de voyelles (langue ouverte)
    vowels = sum(c in "aeiouy" for c in w)
    if vowels / len(w) < 0.25:            return False
    return True


# ---------------------------------------------------------------------------
# Lecture / écriture du dictionnaire unifié
# ---------------------------------------------------------------------------

def load_dict() -> set:
    """Charge data/corpus/dictionary.json et retourne un set de mots."""
    if not DICT.exists():
        return set()
    with open(DICT, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data) if isinstance(data, list) else set()


def save_dict(words: set, label: str = "") -> None:
    """
    Fusionne `words` avec le dictionnaire existant et sauvegarde.
    Thread-safe sur lecture / écriture séquentielle (scripts non concurrents).
    """
    existing = load_dict()
    merged = sorted(existing | {w.lower().strip() for w in words})
    DICT.parent.mkdir(parents=True, exist_ok=True)
    with open(DICT, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    added = len(merged) - len(existing)
    tag = f"[{label}] " if label else ""
    print(f"{tag}+{added} nouveaux mots -> total {len(merged)} dans dictionary.json")
