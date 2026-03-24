import requests
from bs4 import BeautifulSoup
import json
import os
import time
import urllib3

# Désactive les alertes SSL pour éviter le blocage [cite: 47]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from scrape_wiki import is_valid_malagasy 

def get_all_list_links():
    index_url = "https://tenymalagasy.org/bins/alphaLists"
    headers = {'User-Agent': 'Projet_IA_ISPM_Etudiant/1.0'}
    links = []

    try:
        # verify=False pour passer l'erreur de certificat SSL [cite: 47]
        response = requests.get(index_url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            if 'alphaLists' in a['href'] and a['href'] != 'alphaLists':
                full_url = f"https://tenymalagasy.org{a['href']}"
                if full_url not in links:
                    links.append(full_url)
    except Exception as e:
        print(f"Erreur lors de la lecture de l'index : {e}")
    
    return links

def scrape_words_from_link(url):
    headers = {'User-Agent': 'Projet_IA_ISPM_Etudiant/1.0'}
    words_found = set()
    try:
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On cible les balises <b> qui contiennent les entrées de dictionnaire sur ce site 
        for b in soup.find_all('b'):
            word = b.text.strip()
            if is_valid_malagasy(word): 
                words_found.add(word.lower())
    except Exception as e:
        print(f"Erreur sur {url} : {e}")
    return words_found

def main():
    print("1. Récupération de tous les liens de l'index...")
    all_links = get_all_list_links()
    print(f"Nombre de pages à parcourir : {len(all_links)}")

    final_lexicon = set()
    
    for i, link in enumerate(all_links):
        print(f"[{i+1}/{len(all_links)}] Scraping : {link}")
        new_words = scrape_words_from_link(link)
        final_lexicon.update(new_words)
        
        time.sleep(0.5)

    # Sauvegarde finale dans /data 
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, 'data', 'dico.json')
    
    # Charger l'existant pour fusionner  
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            final_lexicon.update(existing)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(final_lexicon)), f, ensure_ascii=False, indent=4)
    
    print(f"\nTerminé ! Dictionnaire total : {len(final_lexicon)} mots.")

if __name__ == "__main__":
    main()