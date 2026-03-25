"""
scrape_jw.py
============
Collecte de vocabulaire malagasy depuis JW.org (section malagasy).

Explore les pages de liste (livres, revues, articles) et suit les liens
internes pour extraire un maximum de texte.

Sortie :
  data/corpus/dictionary.json  ← mots filtrés (fusionnés via _filter)

Usage :
  py scripts/scrape_jw.py
"""

import re
import time

import requests
from bs4 import BeautifulSoup
from _filter import is_valid_malagasy, save_dict, ROOT

HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}
BASE = "https://www.jw.org"
CORPUS_OUT = ROOT / "data" / "corpus" / "jw_mg.txt"

SOURCES = [
    (f"{BASE}/mg/zavatra-misy/boky/", "Boky"),
    (f"{BASE}/mg/zavatra-misy/gazety/", "Gazety"),
    (f"{BASE}/mg/zavatra-misy/lahatsoratra/", "Lahatsoratra"),
]


def _get(url: str, timeout: int = 20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ERREUR {url}: {e}")
        return None


def _extract_text(soup) -> str:
    """Extrait le texte brut des balises de contenu."""
    parts = []
    for tag in soup.find_all(["p", "h1", "h2", "h3", "li", "div"],
                              class_=lambda c: c is None or "publicationText" in str(c)):
        txt = tag.get_text(" ", strip=True)
        if len(txt) > 20:
            parts.append(txt)
    return "\n".join(parts)


def _extract_words(soup) -> tuple:
    """Retourne (set de mots valides, texte brut)."""
    words = set()
    text = _extract_text(soup)
    for w in re.findall(r"\b[a-zA-ZôÔâÂîÎ]+\b", text):
        if is_valid_malagasy(w):
            words.add(w.lower())
    return words, text


_SKIP_PATTERNS = {"choose-language", "preferences", "login", "signup",
                   "search", "sitemap", "legal", "contact", "cookie",
                   "download", "share", "print", "session"}


def _internal_links(soup, limit: int = 50) -> list:
    seen, links = set(), []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if (href.startswith("/mg/")
                and href not in seen
                and not any(skip in href for skip in _SKIP_PATTERNS)
                and "?" not in href):
            seen.add(href)
            links.append(BASE + href)
            if len(links) >= limit:
                break
    return links


def scrape_section(url: str, label: str, follow_limit: int = 50) -> tuple:
    print(f"\n--- {label} : {url} ---")
    soup = _get(url)
    if not soup:
        return set(), []

    words, text = _extract_words(soup)
    texts = [text] if text else []
    print(f"  page liste : {len(words)} mots")

    sub_links = _internal_links(soup, limit=follow_limit)
    for i, link in enumerate(sub_links):
        sub_soup = _get(link)
        if sub_soup:
            new_words, new_text = _extract_words(sub_soup)
            words.update(new_words)
            if new_text:
                texts.append(new_text)
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(sub_links)}] total {len(words)}")
        time.sleep(0.4)

    print(f"  {label} terminé : {len(words)} mots, {len(texts)} pages de texte")
    return words, texts


def main():
    print("=== JW.org Malagasy ===")
    all_words: set = set()
    all_texts: list = []
    for url, label in SOURCES:
        words, texts = scrape_section(url, label)
        all_words.update(words)
        all_texts.extend(texts)

    save_dict(all_words, "jw.org")

    # Sauvegarder le corpus texte pour le n-gram
    if all_texts:
        combined = "\n".join(all_texts)
        CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(CORPUS_OUT, "w", encoding="utf-8") as f:
            f.write(combined)
        print(f"\nCorpus texte → {CORPUS_OUT.name} ({len(combined)//1024} Ko)")


if __name__ == "__main__":
    main()