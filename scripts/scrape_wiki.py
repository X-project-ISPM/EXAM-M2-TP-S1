import requests
import json
import os
import re

def is_valid_malagasy(word):
    """Filtre strict"""
    word = word.lower()
    
    # 1. Longueur minimale (élimine le bruit)
    if len(word) < 2 or not word.isalpha():
        return False

    # 2. Combinaisons interdites
    forbidden = ['nb', 'mk', 'dt', 'bp', 'sz']
    if any(p in word for p in forbidden):
        return False
    
    # 3. 'nk' interdit au début
    if word.startswith('nk'):
        return False

    # 4. Vérification des voyelles
    if not any(v in word for v in 'aeiouy'):
        return False

    return True

def collect_real_text():
    url = "https://mg.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'ProjetML2_ISPM/1.0 (etudiant@ispm.mg)'}
    
    # Paramètres pour obtenir du texte brut
    params = {
        "action": "query",
        "format": "json",
        "generator": "random", # pages au hasard pour varier le vocabulaire
        "grnnamespace": 0,
        "prop": "extracts",
        "explaintext": True,
        "grnlimit": 20 # Nombre de pages par requête
    }
    
    lexicon = set()

    for i in range(15): # accumulation du texte
        try:
            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            for page_id in pages:
                content = pages[page_id].get("extract", "")
                # Extraction de chaque mot du texte
                words = re.findall(r'\b\w+\b', content)
                for w in words:
                    if is_valid_malagasy(w):
                        lexicon.add(w.lower())
            
            print(f"Passage {i+1}: {len(lexicon)} mots uniques en base.")
        except Exception as e:
            print(f"Erreur: {e}")
            break

    # Sauvegarde
    os.makedirs('data', exist_ok=True)
    with open('data/dico.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(list(lexicon)), f, ensure_ascii=False, indent=4)
    
if __name__ == "__main__":
    collect_real_text()