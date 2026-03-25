"""
extract_roots.py
================
Enrichit data/corpus/dictionary.json en extrayant les racines morphologiques
des mots déjà présents, selon les règles de nasalisation et de préfixation
du Malagasy.

Usage :
  py scripts/extract_roots.py

Après exécution, lancez :
  py scripts/build_dictionary.py   ← nettoie et copie vers le backend
"""

from _filter import is_valid_malagasy, load_dict, save_dict


# ---------------------------------------------------------------------------
# Extraction de racines
# ---------------------------------------------------------------------------

def get_root_candidates(word: str) -> set:
    """
    Retourne les candidats-racines pour un mot malagasy fléchi.
    Gère :
      - Préfixes simples (mi-, ma-, fi-, fan-, fam-, voa-, ta-, …)
      - Nasalisation complexe (man-/mam-/many- avec mutation consonantique)
      - Suffixes courants (-ana, -ina, -tra, -iny, -any, -nao, -ko, -ny, -areo)
    """
    # Préfixes complexes → nasalisation : lettre de surface → origines possibles
    prefixes_complex = {
        'man':  ['s', 'z', 't', 'd'],   # man + soratra = manoratra
        'mam':  ['p', 'b', 'f'],        # mam + pangady = mampangady
        'many': ['h', 'k'],             # many + hazakazaka = manyazakazaka (rare)
    }

    # Préfixes simples : retrait direct
    prefixes_simple = [
        'mpampan', 'mampan', 'mampi', 'mampaha',
        'mamp', 'maha', 'mpan', 'mpam', 'mpa',
        'anamp', 'amp',
        'fampan', 'fampi',
        'mi', 'ma', 'fam', 'fan', 'fi',
        'an', 'am',
        'voa', 'ta',
    ]

    # Suffixes à tenter de supprimer
    suffixes = ['areo', 'ana', 'ina', 'tra', 'dra', 'iny', 'any', 'nao', 'ko', 'ny', 'na']

    candidates = set()
    w = word.lower().strip()

    # ---- Préfixes simples ----
    for pref in prefixes_simple:
        if w.startswith(pref) and len(w) > len(pref) + 2:
            rest = w[len(pref):]
            candidates.add(rest)
            # + suppression suffixe sur le reste
            for suf in suffixes:
                if rest.endswith(suf) and len(rest) - len(suf) >= 3:
                    candidates.add(rest[: -len(suf)])

    # ---- Nasalisation ----
    for pref, letters in prefixes_complex.items():
        if w.startswith(pref):
            base = w[len(pref):]
            if len(base) >= 2:
                candidates.add(base)
                for letter in letters:
                    candidates.add(letter + base)

    # ---- Suffixes seuls (sans préfixe) ----
    for suf in suffixes:
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            candidates.add(w[: -len(suf)])

    return candidates


# ---------------------------------------------------------------------------
# Script principal
# ---------------------------------------------------------------------------

def enrich_dictionary_with_roots():
    lexicon = load_dict()

    if not lexicon:
        print("Erreur : dictionnaire vide ou introuvable.")
        return

    print(f"Volume initial : {len(lexicon)} mots.")

    new_roots: set = set()
    for word in list(lexicon):
        for candidate in get_root_candidates(word):
            if is_valid_malagasy(candidate) and candidate not in lexicon:
                new_roots.add(candidate)

    print(f"Nouvelles racines extraites : {len(new_roots)}")
    save_dict(new_roots, "extract_roots")


if __name__ == "__main__":
    enrich_dictionary_with_roots()