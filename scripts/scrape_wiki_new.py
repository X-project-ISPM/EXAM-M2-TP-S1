"""
scrape_wiki.py
==============
Collecte de texte et vocabulaire depuis Wikipedia Malagasy (mg.wikipedia.org).

Sortie :
  data/corpus/dictionary.json  ← mots filtrés (fusionnés avec l'existant)
  data/corpus/wiki_mg.txt      ← texte brut pour n-gram

Usage :
  py scripts/scrape_wiki.py              # dictionnaire + corpus
  py scripts/scrape_wiki.py --pages 500  # plus de pages
"""

import argparse
import re
import time
from pathlib import Path

import requests
from _filter import is_valid_malagasy, save_dict, ROOT

# ---------------------------------------------------------------------------
API_URL = "https://mg.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}

CATEGORIES = [
    "Hafarana", "Fisiana", "Tontolo_iainana",
    "Tantara", "Jeografia", "Fanjakana", "Siansa",
    "Fivavahana", "Kolontsaina", "Fahasalamana", "Politika",
    "Toe-karena", "Teny_malagasy",
]

CORPUS_OUT = ROOT / "data" / "corpus" / "wiki_mg.txt"


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def get_category_pages(category: str, limit: int = 50) -> list:
    params = {
        "action": "query", "format": "json",
        "list": "categorymembers",
        "cmtitle": f"Sokajy:{category}",
        "cmlimit": limit, "cmtype": "page",
    }
    try:
        r = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
        return [m["title"] for m in r.json().get("query", {}).get("categorymembers", [])]
    except Exception as e:
        print(f"  {category}: {e}")
        return []


def get_random_pages(n: int = 50) -> list:
    params = {
        "action": "query", "format": "json",
        "list": "random", "rnnamespace": 0,
        "rnlimit": min(n, 500),
    }
    try:
        r = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
        return [p["title"] for p in r.json().get("query", {}).get("random", [])]
    except Exception as e:
        print(f"  random: {e}")
        return []


def fetch_extracts(titles: list) -> list:
    texts = []
    for i in range(0, len(titles), 20):
        batch = titles[i:i + 20]
        params = {
            "action": "query", "format": "json",
            "titles": "|".join(batch),
            "prop": "extracts", "explaintext": True, "exlimit": "max",
        }
        try:
            r = requests.get(API_URL, params=params, headers=HEADERS, timeout=20)
            for page in r.json().get("query", {}).get("pages", {}).values():
                extract = page.get("extract", "")
                if extract and len(extract) > 100:
                    texts.append(extract)
        except Exception as e:
            print(f"  fetch: {e}")
        time.sleep(0.5)
    return texts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def collect(target_pages: int):
    print(f"=== Wikipedia Malagasy — {target_pages} pages cibles ===\n")

    titles: list = []
    print("Catégories :")
    for cat in CATEGORIES:
        pages = get_category_pages(cat)
        titles.extend(pages)
        print(f"  {cat}: {len(pages)}")
        time.sleep(0.3)

    remaining = max(0, target_pages - len(titles))
    if remaining:
        print(f"\n+ {remaining} pages aléatoires")
        titles.extend(get_random_pages(remaining))

    titles = list(dict.fromkeys(titles))
    print(f"\nTitres uniques : {len(titles)}")

    texts = fetch_extracts(titles)
    combined = "\n".join(texts)
    tokens = re.findall(r'\b[a-zA-ZôÔâÂîÎ]+\b', combined)
    print(f"Tokens bruts : {len(tokens)}")

    # Corpus texte (n-gram)
    CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(CORPUS_OUT, "w", encoding="utf-8") as f:
        f.write(combined)
    print(f"Corpus → {CORPUS_OUT.relative_to(ROOT)} ({CORPUS_OUT.stat().st_size // 1024} Ko)")

    # Dictionnaire
    valid = {w.lower() for w in tokens if is_valid_malagasy(w)}
    print(f"Mots filtrés : {len(valid)}")
    save_dict(valid, "wiki")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=300)
    args = parser.parse_args()
    collect(args.pages)
