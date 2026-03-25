"""
scrape_gazetiko.py
==================
Collecte de texte malagasy depuis Gazetiko.mg (agrégateur de nouvelles malgaches).

Sortie :
  data/corpus/dictionary.json    ← mots filtrés (fusionnés via _filter)
  data/corpus/gazetiko_mg.txt    ← texte brut pour n-gram

Usage :
  py scripts/scrape_gazetiko.py              # 10 pages d'index par défaut
  py scripts/scrape_gazetiko.py --pages 30
"""

import argparse
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from _filter import is_valid_malagasy, save_dict, ROOT

HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}
BASE = "https://gazetiko.mg"
CORPUS_OUT = ROOT / "data" / "corpus" / "gazetiko_mg.txt"

_SKIP_PATTERNS = {"login", "signup", "register", "subscribe", "account",
                   "search", "sitemap", "contact", "about", "politique",
                   "mentions", "cookie", "privacy"}


def _get(url: str, timeout: int = 20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ERREUR {url}: {e}")
        return None


def get_article_links_from_page(page_num: int) -> list:
    """Scrape les liens d'article depuis une page de liste."""
    if page_num == 1:
        url = f"{BASE}/"
    else:
        url = f"{BASE}/page/{page_num}/"

    soup = _get(url)
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Articles sur gazetiko ont généralement un slug avec date ou catégorie
        if (href.startswith(BASE + "/")
                and href != BASE + "/"
                and not any(skip in href for skip in _SKIP_PATTERNS)
                and "?" not in href
                and href.count("/") >= 4  # au moins 3 niveaux de chemin
                and href not in links):
            links.append(href)
    return links


def extract_text(url: str) -> str:
    """Extrait le texte du corps d'un article."""
    soup = _get(url)
    if not soup:
        return ""

    parts = []
    # Chercher le contenu principal
    main = (soup.find("div", class_=re.compile(r"entry-content|article-content|post-content|content-body"))
            or soup.find("article")
            or soup.find("main"))
    if main:
        for tag in main.find_all(["p", "h1", "h2", "h3", "li"]):
            txt = tag.get_text(" ", strip=True)
            if len(txt) > 25:
                parts.append(txt)
    else:
        for p in soup.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if len(txt) > 30:
                parts.append(txt)
    return "\n".join(parts)


def collect(target_pages: int):
    print(f"=== Gazetiko.mg — {target_pages} pages ===\n")

    all_urls = []
    consecutive_empty = 0

    for page_num in range(1, target_pages + 1):
        links = get_article_links_from_page(page_num)
        new = [l for l in links if l not in all_urls]
        if not new:
            consecutive_empty += 1
            if consecutive_empty >= 3:
                print(f"  Arrêt à la page {page_num} (3 pages vides)")
                break
            continue
        consecutive_empty = 0
        all_urls.extend(new)
        if page_num % 5 == 0 or page_num == 1:
            print(f"  Page {page_num}: {len(new)} nouveaux liens (total: {len(all_urls)})")
        time.sleep(0.4)

    print(f"\nArticles trouvés : {len(all_urls)}")
    if not all_urls:
        print("Aucun article trouvé — le site a peut-être une structure différente.")
        return

    # Extraction avec sauvegarde incrémentale
    CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
    if CORPUS_OUT.exists():
        CORPUS_OUT.unlink()

    all_words = set()
    article_count = 0

    try:
        with open(CORPUS_OUT, "a", encoding="utf-8") as fout:
            for i, url in enumerate(all_urls):
                text = extract_text(url)
                if text:
                    fout.write(text + "\n")
                    article_count += 1
                    for w in re.findall(r"\b[a-zA-ZôÔâÂîÎ]+\b", text):
                        if is_valid_malagasy(w):
                            all_words.add(w.lower())

                if (i + 1) % 20 == 0:
                    fout.flush()
                    print(f"  [{i+1}/{len(all_urls)}] {len(all_words)} mots, {article_count} textes")
                time.sleep(0.4)
    except KeyboardInterrupt:
        print(f"\n  Interrompu à [{article_count}] — données partielles sauvegardées.")

    print(f"\nTotal : {len(all_words)} mots, {article_count} articles")

    if CORPUS_OUT.exists() and CORPUS_OUT.stat().st_size > 0:
        size_kb = CORPUS_OUT.stat().st_size // 1024
        tokens = re.findall(r'\b[a-zA-ZôÔâÂîÎ]+\b',
                             CORPUS_OUT.read_text(encoding="utf-8"))
        print(f"Corpus → {CORPUS_OUT.name} ({size_kb} Ko, {len(tokens):,} tokens)")

    if all_words:
        save_dict(all_words, "gazetiko")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=10)
    args = parser.parse_args()
    collect(args.pages)
