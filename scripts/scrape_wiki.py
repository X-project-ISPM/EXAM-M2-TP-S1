import requests
import json
import os
import re

def is_valid_malagasy(word):
    """Filtre strict selon les règles du TP et la phonétique[cite: 17, 51]."""
    word = word.lower()
    
    # 1. Longueur minimale (élimine le bruit)
    if len(word) < 2 or not word.isalpha():
        return False

    # 2. Combinaisons interdites du sujet [cite: 51]
    forbidden = ['nb', 'mk', 'dt', 'bp', 'sz']
    if any(p in word for p in forbidden):
        return False
    
    # 3. 'nk' interdit au début [cite: 51]
    if word.startswith('nk'):
        return False

    # 4. Vérification des voyelles (essentiel en malagasy)
    if not any(v in word for v in 'aeiouy'):
        return False

    return True

def collect_real_text():
    url = "https://mg.wikipedia.org/w/api.php"
    headers = {'User-Agent': 'ProjetML2_ISPM/1.0 (etudiant@ispm.mg)'}
    
    # Paramètres pour obtenir du texte brut (plain text)
    params = {
        "action": "query",
        "format": "json",
        "generator": "random", # On prend des pages au hasard pour varier le vocabulaire
        "grnnamespace": 0,
        "prop": "extracts",
        "explaintext": True,
        "grnlimit": 20 # Nombre de pages par requête
    }
    
    lexicon = set()
    print("Extraction de texte réel en cours...")

    for i in range(15): # Répéter pour accumuler du texte
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
    with open('data/dictionnaire_riche.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(list(lexicon)), f, ensure_ascii=False, indent=4)
    
    print(f"\nFélicitations ! Votre dictionnaire contient {len(lexicon)} mots réels.")

if __name__ == "__main__":
    collect_real_text()