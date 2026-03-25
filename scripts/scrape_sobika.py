"""
scrape_sobika.py
================
Collecte de texte malagasy depuis Sobika.com (portail communautaire malgache).

Sobika contient des articles de news, forum, et rubriques culturelles en malagasy.

Sortie :
  data/corpus/dictionary.json  ← mots filtrés (fusionnés via _filter)
  data/corpus/sobika_mg.txt    ← texte brut pour n-gram

Usage :
  py scripts/scrape_sobika.py              # 20 pages par catégorie par défaut
  py scripts/scrape_sobika.py --pages 50
"""

import argparse
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from _filter import is_valid_malagasy, save_dict, ROOT

HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}
BASE = "https://www.sobika.com"
CORPUS_OUT = ROOT / "data" / "corpus" / "sobika_mg.txt"

_SKIP_PATTERNS = {"login", "signup", "register", "account", "basket", "cart",
                   "newsletter", "search", "sitemap", "contact", "about",
                   "mentions", "cookie", "privacy", "password", "profil"}


def _get(url: str, timeout: int = 20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ERREUR {url}: {e}")
        return None


def discover_article_links(soup, seen: set) -> list:
    """Extrait tous les liens vers des articles/pages de contenu."""
    links = []
    if not soup:
        return links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            href = BASE + href
        if (href.startswith(BASE)
                and href not in seen
                and not any(s in href.lower() for s in _SKIP_PATTERNS)
                and "?" not in href
                and href.count("/") >= 4):
            seen.add(href)
            links.append(href)
    return links


def extract_text(url: str) -> str:
    """Extrait le texte d'une page Sobika."""
    soup = _get(url)
    if not soup:
        return ""

    parts = []
    # Cherche les zones de contenu principales
    for selector in [
        {"class_": re.compile(r"article|content|post|entry|texte|contenu|body")},
        {"name": "article"},
        {"name": "main"},
    ]:
        container = soup.find(True, **selector) if "class_" in selector else soup.find(selector.get("name"))
        if container:
            for tag in container.find_all(["p", "h2", "h3", "li", "div"]):
                # Éviter la récursion des divs
                if tag.name == "div" and tag.find(["p", "h2", "h3"]):
                    continue
                txt = tag.get_text(" ", strip=True)
                if len(txt) > 30 and not any(s in txt.lower() for s in ["cookie", "newsletter", "©"]):
                    parts.append(txt)
            if parts:
                break

    if not parts:
        # Fallback simple
        for p in soup.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if len(txt) > 40:
                parts.append(txt)

    return "\n".join(parts)


def collect(target_pages: int):
    print(f"=== Sobika.com — exploration multi-pages ===\n")

    # Partir de la page d'accueil
    home = _get(BASE + "/")
    if not home:
        print("Site inaccessible.")
        return

    seen = {BASE + "/"}
    queue = discover_article_links(home, seen)
    print(f"Page d'accueil : {len(queue)} liens trouvés")

    # Exploration en largeur jusqu'à target_pages liens
    all_links = list(queue)
    i = 0
    while i < len(all_links) and len(all_links) < target_pages * 10:
        url = all_links[i]
        sub_soup = _get(url)
        if sub_soup:
            new_links = discover_article_links(sub_soup, seen)
            all_links.extend(new_links[:20])  # Max 20 liens par page pour éviter l'explosion
        i += 1
        if i % 10 == 0:
            print(f"  Exploration [{i}] : {len(all_links)} liens découverts")
        time.sleep(0.3)
        if len(all_links) >= target_pages * 10:
            break

    all_links = all_links[:target_pages * 10]
    print(f"\nLiens à extraire : {len(all_links)}")

    # Extraction du contenu avec sauvegarde incrémentale
    CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
    if CORPUS_OUT.exists():
        CORPUS_OUT.unlink()

    all_words = set()
    article_count = 0

    try:
        with open(CORPUS_OUT, "a", encoding="utf-8") as fout:
            for j, url in enumerate(all_links):
                text = extract_text(url)
                if text:
                    fout.write(text + "\n")
                    article_count += 1
                    for w in re.findall(r"\b[a-zA-ZôÔâÂîÎ]+\b", text):
                        if is_valid_malagasy(w):
                            all_words.add(w.lower())

                if (j + 1) % 20 == 0:
                    fout.flush()
                    print(f"  [{j+1}/{len(all_links)}] {len(all_words)} mots, {article_count} pages utiles")
                time.sleep(0.4)
    except KeyboardInterrupt:
        print(f"\n  Interrompu à [{article_count}] — données partielles sauvegardées.")

    print(f"\nTotal : {len(all_words)} mots, {article_count} pages avec texte")

    if CORPUS_OUT.exists() and CORPUS_OUT.stat().st_size > 0:
        size_kb = CORPUS_OUT.stat().st_size // 1024
        tokens = re.findall(r'\b[a-zA-ZôÔâÂîÎ]+\b',
                             CORPUS_OUT.read_text(encoding="utf-8"))
        print(f"Corpus → {CORPUS_OUT.name} ({size_kb} Ko, {len(tokens):,} tokens)")

    if all_words:
        save_dict(all_words, "sobika")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=20,
                        help="Nombre de pages à parcourir (x10 liens par page)")
    args = parser.parse_args()
    collect(args.pages)
