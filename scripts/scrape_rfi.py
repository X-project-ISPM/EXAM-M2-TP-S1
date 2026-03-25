"""
scrape_rfi.py
=============
Collecte de texte malagasy depuis RFI Malagasy (malagasy.rfi.fr).

RFI Malagasy publie quotidiennement des articles d'actualité politique,
culturelle et sociale en langue malagasy.

Sortie :
  data/corpus/dictionary.json  ← mots filtrés (fusionnés via _filter)
  data/corpus/rfi_mg.txt       ← texte brut pour n-gram

Usage :
  py scripts/scrape_rfi.py              # 50 pages par défaut
  py scripts/scrape_rfi.py --pages 100
"""

import argparse
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from _filter import is_valid_malagasy, save_dict, ROOT

HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}
BASE = "https://malagasy.rfi.fr"
CORPUS_OUT = ROOT / "data" / "corpus" / "rfi_mg.txt"

# Sections avec contenu malagasy
SECTIONS = [
    "/mg/afrique",
    "/mg/mondial",
    "/mg/culture",
    "/mg/sport",
    "/mg/economie",
    "/mg/sante",
    "/mg/science",
]

_SKIP_PATTERNS = {"login", "signup", "subscribe", "contact", "about", "rfi-monde",
                   "newsletter", "sitemap", "cookie", "legal", "mentions"}


def _get(url: str, timeout: int = 20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ERREUR {url}: {e}")
        return None


def get_article_links(section: str, page: int = 1) -> list:
    """Récupère les liens d'articles d'une section."""
    url = f"{BASE}{section}" if page == 1 else f"{BASE}{section}?p={page}"
    soup = _get(url)
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Normaliser les URLs relatives
        if href.startswith("/mg/") and not any(s in href for s in _SKIP_PATTERNS):
            full = BASE + href
            if full not in links and "?" not in href:
                links.append(full)
        elif href.startswith(BASE + "/mg/") and not any(s in href for s in _SKIP_PATTERNS):
            if href not in links and "?" not in href:
                links.append(href)
    return links


def extract_article_text(url: str) -> str:
    """Extrait le texte du corps d'un article RFI."""
    soup = _get(url)
    if not soup:
        return ""

    parts = []
    # RFI utilise des articles structurés
    article = soup.find("div", class_=re.compile(r"article-content|m-content|entry-content|o-text-article"))
    if not article:
        article = soup.find("article")
    if not article:
        article = soup.find("main")

    if article:
        for tag in article.find_all(["p", "h2", "h3", "li"]):
            txt = tag.get_text(" ", strip=True)
            if len(txt) > 20:
                parts.append(txt)
    else:
        # Fallback
        for p in soup.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if len(txt) > 30 and not any(s in txt.lower() for s in ["cookie", "newsletter", "rfi"]):
                parts.append(txt)

    return "\n".join(parts)


def collect(target_pages: int):
    print(f"=== RFI Malagasy — {target_pages} pages par section ===\n")

    all_urls = []
    print("Collecte des liens par section :")
    for section in SECTIONS:
        section_links = []
        for page in range(1, target_pages + 1):
            links = get_article_links(section, page)
            new = [l for l in links if l not in all_urls and l not in section_links]
            section_links.extend(new)
            if not new and page > 1:
                break
            time.sleep(0.3)
        all_urls.extend(section_links)
        print(f"  {section}: {len(section_links)} articles")
        time.sleep(0.3)

    # Dédoublonner
    all_urls = list(dict.fromkeys(all_urls))
    print(f"\nTotal articles uniques : {len(all_urls)}")
    if not all_urls:
        print("Aucun article trouvé. Vérifiez la connectivité vers malagasy.rfi.fr")
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
                text = extract_article_text(url)
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
        print(f"\n  Interrompu à [{article_count}] articles — données sauvegardées.")

    print(f"\nTotal : {len(all_words)} mots, {article_count} articles")

    if CORPUS_OUT.exists() and CORPUS_OUT.stat().st_size > 0:
        size_kb = CORPUS_OUT.stat().st_size // 1024
        tokens = re.findall(r'\b[a-zA-ZôÔâÂîÎ]+\b',
                             CORPUS_OUT.read_text(encoding="utf-8"))
        print(f"Corpus → {CORPUS_OUT.name} ({size_kb} Ko, {len(tokens):,} tokens)")

    if all_words:
        save_dict(all_words, "rfi")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=50,
                        help="Nombre de pages par section")
    args = parser.parse_args()
    collect(args.pages)
