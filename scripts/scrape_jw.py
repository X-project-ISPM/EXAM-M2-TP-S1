import requests
from bs4 import BeautifulSoup
import json
import os
import re

from scrape_wiki import is_valid_malagasy 

def scrape_jw_source(url, label):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Projet_ISPM_NLP/1.0'}
    new_words = set()
    
    print(f"Extraction des {label} sur JW.org...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On récupère tout le texte informatif pour enrichir le lexique
        text_elements = soup.find_all(['h3', 'div'], class_=['synopsis', 'publicationText'])
        
        for element in text_elements:
            # Extraction des mots individuels
            words = re.findall(r'\b\w+\b', element.text)
            for w in words:
                if is_valid_malagasy(w):
                    new_words.add(w.lower())
                    
        return new_words
    except Exception as e:
        print(f"Erreur lors du scraping de {label}: {e}")
        return set()

def merge_to_rich_dictionary(words_to_add):
    # Gestion du chemin relatif pour pointer vers /data à la racine
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, 'data', 'dico.json')
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    lexicon = set()
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            lexicon = set(json.load(f))
    
    lexicon.update(words_to_add)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(lexicon)), f, ensure_ascii=False, indent=4)
    
    print(f"Mise à jour effectuée : {len(lexicon)} mots au total dans le dictionnaire.")

if __name__ == "__main__":
    sources = [
        ("https://www.jw.org/mg/zavatra-misy/boky/", "Livres (Boky)"),
        ("https://www.jw.org/mg/zavatra-misy/gazety/", "Revues (Gazety)")
    ]
    
    all_new_words = set()
    for url, label in sources:
        words = scrape_jw_source(url, label)
        all_new_words.update(words)
    
    merge_to_rich_dictionary(all_new_words)