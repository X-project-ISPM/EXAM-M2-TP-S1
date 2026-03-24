import json
import os

def get_root_candidates(word):
    """
    Tente d'extraire la racine en gérant les règles de nasalisation
    spécifiques au Malagasy (ex: man- + s -> manoratra).
    """
    prefixes_complex = {
        'man': ['s', 'z', 't', 'd'], # n remplace souvent s, z, t, d
        'mam': ['p', 'b', 'f'],      # m remplace souvent p, b, f
        'many': ['h', 'k']           # ny remplace souvent h, k
    }
    
    prefixes_simple = ['mi', 'mamp', 'mampan', 'maha', 'fi', 'fan', 'fam', 'voa', 'ta']
    
    candidates = set()
    
    # Cas 1 : Préfixes simples (on coupe juste)
    for pref in prefixes_simple:
        if word.startswith(pref) and len(word) > len(pref) + 2:
            candidates.add(word[len(pref):])

    # Cas 2 : Nasalisation (cas plus complexes)
    for pref, letters in prefixes_complex.items():
        if word.startswith(pref):
            base = word[len(pref):]
            if len(base) >= 2:
                # On ajoute la base telle quelle (ex: manoratra -> oratra)
                candidates.add(base)
                # On tente de restaurer la lettre disparue (ex: manoratra -> soratra)
                for l in letters:
                    candidates.add(l + base)
                    
    return candidates

def enrich_dictionary_with_roots():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, 'data', 'dico.json')

    if not os.path.exists(path):
        print("Erreur : dico.json introuvable.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        lexicon = set(json.load(f))

    print(f"Volume initial : {len(lexicon)} mots.")
    
    new_roots = set()
    for word in list(lexicon):
        candidates = get_root_candidates(word)
        for cand in candidates:
            # On n'ajoute que si la racine candidate respecte vos filtres phonotactiques
            from scrape_wiki import is_valid_malagasy
            if is_valid_malagasy(cand):
                new_roots.add(cand)

    # Fusion finale
    final_lexicon = lexicon.union(new_roots)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(final_lexicon)), f, ensure_ascii=False, indent=4)
    
    print(f"Racines extraites et ajoutées : {len(new_roots)}")
    print(f"Nouveau volume total : {len(final_lexicon)} mots.")

if __name__ == "__main__":
    enrich_dictionary_with_roots()