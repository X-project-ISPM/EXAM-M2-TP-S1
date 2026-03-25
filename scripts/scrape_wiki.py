"""
scrape_wiki.py
==============
Collecte de texte et vocabulaire depuis Wikipedia Malagasy (mg.wikipedia.org).
Utilise l'API allpages pour parcourir systematiquement tous les articles.

Sortie :
  data/corpus/dictionary.json  <- mots filtres (fusionnes avec l'existant)
  data/corpus/wiki_mg.txt      <- texte brut pour n-gram

Usage :
  py scripts/scrape_wiki.py              # 5000 articles par defaut
  py scripts/scrape_wiki.py --pages 20000
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
CORPUS_OUT = ROOT / "data" / "corpus" / "wiki_mg.txt"


def get_all_page_titles(target: int) -> list:
    """Recupere les titres d'articles via API allpages (systematique)."""
    titles = []
    apcontinue = ""
    while len(titles) < target:
        params = {
            "action": "query", "format": "json",
            "list": "allpages",
            "aplimit": min(500, target - len(titles)),
            "apnamespace": 0,
            "apfilterredir": "nonredirects",
        }
        if apcontinue:
            params["apcontinue"] = apcontinue
        try:
            r = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
            data = r.json()
            pages = data.get("query", {}).get("allpages", [])
            titles.extend(p["title"] for p in pages)
            cont = data.get("continue", {})
            apcontinue = cont.get("apcontinue", "")
            if not apcontinue:
                break
        except Exception as e:
            print(f"  allpages erreur: {e}")
            break
        time.sleep(0.2)
    return titles[:target]


def fetch_extracts(titles: list, corpus_file, all_words: set) -> int:
    """Recupere les extraits texte par lots de 50, sauvegarde incrementale."""
    text_count = 0
    for i in range(0, len(titles), 50):
        batch = titles[i:i + 50]
        params = {
            "action": "query", "format": "json",
            "titles": "|".join(batch),
            "prop": "extracts", "explaintext": True, "exlimit": "max",
            "exchars": 2000,
        }
        try:
            r = requests.get(API_URL, params=params, headers=HEADERS, timeout=20)
            for page in r.json().get("query", {}).get("pages", {}).values():
                extract = page.get("extract", "")
                if extract and len(extract) > 50:
                    corpus_file.write(extract + "\n")
                    text_count += 1
                    for w in re.findall(r"[a-zA-Z\u00f4\u00c4\u00e2\u00c2\u00ee\u00ce]+", extract):
                        if is_valid_malagasy(w):
                            all_words.add(w.lower())
        except KeyboardInterrupt:
            print(f"\n  Interrompu a [{i}/{len(titles)}] -- donnees sauvegardees.")
            return text_count
        except Exception as e:
            print(f"  fetch erreur: {e}")
        if (i + 50) % 1000 == 0:
            corpus_file.flush()
            print(f"  [{i+50}/{len(titles)}] {text_count} articles, {len(all_words)} mots")
        time.sleep(0.3)
    return text_count


def collect(target_pages: int):
    print(f"=== Wikipedia Malagasy -- {target_pages} articles cibles ===\n")
    print("Recuperation des titres d'articles...")
    titles = get_all_page_titles(target_pages)
    print(f"  Titres uniques : {len(titles)}")

    CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
    if CORPUS_OUT.exists():
        CORPUS_OUT.unlink()

    all_words = set()
    try:
        with open(CORPUS_OUT, "a", encoding="utf-8") as f:
            text_count = fetch_extracts(titles, f, all_words)
    except KeyboardInterrupt:
        text_count = 0

    print(f"\nArticles extraits : {text_count}")
    if CORPUS_OUT.exists() and CORPUS_OUT.stat().st_size > 0:
        size_kb = CORPUS_OUT.stat().st_size // 1024
        tokens_n = len(re.findall(r"[a-zA-Z\u00f4\u00c4\u00e2\u00c2\u00ee\u00ce]+",
                                  CORPUS_OUT.read_text(encoding="utf-8")))
        print(f"Corpus -> {CORPUS_OUT.relative_to(ROOT)} ({size_kb} Ko, {tokens_n:,} tokens)")
    print(f"Mots filtres : {len(all_words)}")
    save_dict(all_words, "wiki")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=5000)
    args = parser.parse_args()
    collect(args.pages)
