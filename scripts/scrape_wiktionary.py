import requests
import json
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from scrape_wiki import is_valid_malagasy
except ImportError:
    def is_valid_malagasy(w): return len(w) > 1

def get_all_wiktionary_pages():
    url = "https://mg.wiktionary.org/w/api.php"
    
    # On demande la liste de TOUTES les pages (allpages)
    params = {
        "action": "query",
        "list": "allpages",
        "aplimit": "500",
        "format": "json",
        "apnamespace": "0" # Uniquement l'espace principal (les mots)
    }
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    all_words = set()
    print("Extraction de l'index complet de mg.wiktionary.org...")

    while True:
        try:
            response = requests.get(url, params=params, headers=headers, verify=False)
            data = response.json()
            
            pages = data.get("query", {}).get("allpages", [])
            if not pages:
                break

            for page in pages:
                word = page["title"]
                if is_valid_malagasy(word):
                    all_words.add(word.lower())
            
            print(f"Mots collectés : {len(all_words)}...", end="\r")
            
            if "continue" in data:
                params.update(data["continue"])
            else:
                break
        except Exception as e:
            print(f"\nErreur : {e}")
            break
            
    return all_words

if __name__ == "__main__":
    mots = get_all_wiktionary_pages()
    if mots:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(base_dir, 'data', 'wiktionary_mots.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sorted(list(mots)), f, ensure_ascii=False, indent=4)
        print(f"\nSuccès ! {len(mots)} mots extraits dans {output_path}")
    else:
        print("\nToujours rien. Vérifie si tu peux accéder à mg.wiktionary.org dans ton navigateur.")