"""
scrape_wiktionary.py
====================
Collecte de vocabulaire et texte depuis le Wiktionnaire malagasy (mg.wiktionary.org).

Utilise l'API MediaWiki pour récupérer les pages de définitions.
Chaque page contient des mots, définitions, et exemples en malagasy.

Sortie :
  data/corpus/dictionary.json     ← mots filtrés (fusionnés via _filter)
  data/corpus/wiktionary_mg.txt   ← texte brut pour n-gram

Usage :
  py scripts/scrape_wiktionary.py              # 2000 pages par défaut
  py scripts/scrape_wiktionary.py --pages 5000
"""

import argparse
import re
import time
from pathlib import Path

import requests
from _filter import is_valid_malagasy, save_dict, ROOT

HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}
API_URL = "https://mg.wiktionary.org/w/api.php"
CORPUS_OUT = ROOT / "data" / "corpus" / "wiktionary_mg.txt"


def get_all_pages(target: int) -> list:
    """Récupère les titres de pages via API allpages (namespace 0 = articles)."""
    titles = []
    apcontinue = ""

    while len(titles) < target:
        params = {
            "action": "query", "format": "json",
            "list": "allpages",
            "aplimit": min(500, target - len(titles)),
            "apnamespace": 0,
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
        time.sleep(0.3)

    print(f"  Titres récupérés : {len(titles)}")
    return titles[:target]


def fetch_page_texts(titles: list, corpus_out: "Path", all_words: set) -> int:
    """Récupère le contenu par lots, sauvegarde de façon incrémentale. Retourne le nb de textes."""
    text_count = 0
    corpus_out.parent.mkdir(parents=True, exist_ok=True)

    with open(corpus_out, "a", encoding="utf-8") as fout:
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
                    if extract and len(extract) > 30:
                        fout.write(extract + "\n")
                        text_count += 1
                        for w in re.findall(r"\b[a-zA-ZôÔâÂîÎ]+\b", extract):
                            if is_valid_malagasy(w):
                                all_words.add(w.lower())
            except KeyboardInterrupt:
                print(f"\n  Interrompu à [{i}/{len(titles)}] — données partielles sauvegardées.")
                return text_count
            except Exception as e:
                print(f"  fetch batch {i}: {e}")
            if (i + 20) % 200 == 0:
                print(f"  [{i+20}/{len(titles)}] {text_count} textes, {len(all_words)} mots")
            time.sleep(0.3)
    return text_count


def collect(target_pages: int):
    print(f"=== Wiktionary Malagasy — {target_pages} pages ===\n")

    # Vider le corpus existant avant de commencer
    CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
    if CORPUS_OUT.exists():
        CORPUS_OUT.unlink()

    titles = get_all_pages(target_pages)
    if not titles:
        print("Aucun titre récupéré.")
        return

    # Les titres eux-mêmes peuvent être des mots malagasy
    all_words = {t.lower() for t in titles if is_valid_malagasy(t)}
    print(f"  Mots valides parmi les titres : {len(all_words)}")

    # Récupérer le texte des pages (avec sauvegarde incrémentale)
    print("\nRécupération du contenu des pages...")
    try:
        text_count = fetch_page_texts(titles, CORPUS_OUT, all_words)
    except KeyboardInterrupt:
        print("  Interruption reçue, sauvegarde en cours...")
        text_count = 0

    print(f"  Pages avec contenu : {text_count}")

    tokens_count = 0
    if CORPUS_OUT.exists():
        tokens_raw = re.findall(r'\b[a-zA-ZôÔâÂîÎ]+\b',
                                 CORPUS_OUT.read_text(encoding="utf-8"))
        tokens_count = len(tokens_raw)
        size_kb = CORPUS_OUT.stat().st_size // 1024
        print(f"  Corpus → {CORPUS_OUT.name} ({size_kb} Ko, {tokens_count:,} tokens)")

    print(f"  Mots uniques valides : {len(all_words)}")

    # Sauvegarder le dictionnaire
    if all_words:
        save_dict(all_words, "wiktionary")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=2000,
                        help="Nombre de pages à récupérer")
    args = parser.parse_args()
    collect(args.pages)
