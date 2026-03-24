import json
import os
import re

def is_pure_malagasy(word):
    word = word.lower().strip()
    
    # 1. Caractères interdits (c, q, u, x)
    if re.search(r'[cqux]', word):
        return False
    
    # 2. Doit se terminer par une voyelle (a, e, i, o, y)
    if not word.endswith(('a', 'e', 'i', 'o', 'y')):
        return False

    # 3. Interdire les doubles consonnes impossibles (ex: rt, st, gl, bl, ph)
    # On autorise uniquement les combinaisons nasales (nt, nd, mp, mb, nk, ng, tr, dr, ts)
    # et les successions de voyelles.
    
    # Liste des suites de consonnes autorisées en malgache
    allowed_clusters = ['nt', 'nd', 'mp', 'mb', 'nk', 'ng', 'tr', 'dr', 'ts', 'nj', 'ny', 'nc']
    
    # On cherche toutes les doubles consonnes
    consonants = "bdfghjklmnprstvwzy"
    clusters = re.findall(r'([^aeiouy]{2,})', word)
    
    for cluster in clusters:
        if cluster not in allowed_clusters:
            # Si on trouve "rt" dans "partie" ou "st" dans "station", on rejette
            return False

    # 4. Longueur minimale
    if len(word) < 2:
        return False

    return True

def clean_my_dict():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, 'data', 'dico.json')
    
    if not os.path.exists(path):
        print("Fichier introuvable.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        dirty_words = json.load(f)

    print(f"Mots avant filtrage : {len(dirty_words)}")
    
    clean_words = [w for w in dirty_words if is_pure_malagasy(w)]
    
    print(f"Mots après filtrage : {len(clean_words)}")
    print(f"Mots supprimés : {len(dirty_words) - len(clean_words)}")

    # Sauvegarde du dictionnaire propre
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sorted(clean_words), f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    clean_my_dict()