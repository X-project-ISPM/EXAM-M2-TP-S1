"""
scrape_globalvoices.py
======================
Collecte de texte et vocabulaire depuis Global Voices Malagasy (mg.globalvoices.org).

Global Voices publie des articles de journalisme citoyen traduits en malagasy.
Le scraper parcourt les pages d'archives paginées, suit chaque article et
extrait le corps du texte.

Sortie :
  data/corpus/dictionary.json  ← mots filtrés (fusionnés via _filter)
  data/corpus/globalvoices_mg.txt ← corpus texte pour n-gram

Usage :
  py scripts/scrape_globalvoices.py              # 50 pages d'archive par défaut
  py scripts/scrape_globalvoices.py --pages 100  # plus de pages
"""

import argparse
import re
import time

import requests
from bs4 import BeautifulSoup
from _filter import is_valid_malagasy, save_dict, ROOT

HEADERS = {"User-Agent": "ProjetML2_ISPM/1.0 (etudiant@ispm.mg)"}
BASE = "https://mg.globalvoices.org"
CORPUS_OUT = ROOT / "data" / "corpus" / "globalvoices_mg.txt"


def _get(url: str, timeout: int = 20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ERREUR {url}: {e}")
        return None


def get_article_links(page_num: int) -> list:
    """Récupère les liens d'articles depuis une page d'archive paginée."""
    url = f"{BASE}/page/{page_num}/" if page_num > 1 else f"{BASE}/"
    soup = _get(url)
    if not soup:
        return []

    links = []
    # Les articles sont dans des balises <article> ou <h2>/<h3> avec des liens
    for a in soup.select("a[href]"):
        href = a["href"]
        # Les URLs d'articles Global Voices ont un format typique avec année/mois
        if (href.startswith(BASE)
                and re.search(r'/\d{4}/\d{2}/\d{2}/', href)
                and href not in links):
            links.append(href)
    return links


def extract_article_text(url: str) -> str:
    """Extrait le texte du corps d'un article."""
    soup = _get(url)
    if not soup:
        return ""

    parts = []
    # Contenu principal de l'article
    entry = soup.find("div", class_=re.compile(r"entry-content|post-body|article-body"))
    if entry:
        for p in entry.find_all(["p", "h2", "h3", "li", "blockquote"]):
            txt = p.get_text(" ", strip=True)
            if len(txt) > 20:
                parts.append(txt)
    else:
        # Fallback : tous les paragraphes de la page
        for p in soup.find_all("p"):
            txt = p.get_text(" ", strip=True)
            if len(txt) > 30:
                parts.append(txt)

    return "\n".join(parts)


def collect(target_pages: int):
    print(f"=== Global Voices Malagasy — {target_pages} pages d'archive ===\n")

    all_article_urls = []
    consecutive_empty = 0

    for page_num in range(1, target_pages + 1):
        links = get_article_links(page_num)
        if not links:
            consecutive_empty += 1
            if consecutive_empty >= 3:
                print(f"  3 pages vides consécutives, arrêt à la page {page_num}")
                break
            continue
        consecutive_empty = 0

        new_links = [l for l in links if l not in all_article_urls]
        all_article_urls.extend(new_links)
        if page_num % 10 == 0 or page_num == 1:
            print(f"  Page {page_num}: {len(new_links)} nouveaux articles (total: {len(all_article_urls)})")
        time.sleep(0.5)

    print(f"\nArticles uniques trouvés : {len(all_article_urls)}")

    # Préparer le fichier corpus (mode append pour reprise en cas d'interruption)
    CORPUS_OUT.parent.mkdir(parents=True, exist_ok=True)
    # Repartir de zéro à chaque lancement
    if CORPUS_OUT.exists():
        CORPUS_OUT.unlink()

    all_words = set()
    article_count = 0

    try:
        with open(CORPUS_OUT, "a", encoding="utf-8") as fout:
            for i, url in enumerate(all_article_urls):
                text = extract_article_text(url)
                if text:
                    fout.write(text + "\n")
                    article_count += 1
                    for w in re.findall(r"\b[a-zA-ZôÔâÂîÎ]+\b", text):
                        if is_valid_malagasy(w):
                            all_words.add(w.lower())

                if (i + 1) % 20 == 0:
                    fout.flush()  # Forcer l'écriture disque
                    print(f"  [{i+1}/{len(all_article_urls)}] {len(all_words)} mots, {article_count} textes")
                time.sleep(0.4)
    except KeyboardInterrupt:
        print(f"\n  Interrompu à [{article_count}/{len(all_article_urls)}] articles — données partielles sauvegardées.")

    print(f"\nTotal : {len(all_words)} mots uniques, {article_count} articles avec texte")

    if CORPUS_OUT.exists() and CORPUS_OUT.stat().st_size > 0:
        tokens = re.findall(r'\b[a-zA-ZôÔâÂîÎ]+\b',
                             CORPUS_OUT.read_text(encoding="utf-8"))
        print(f"Corpus → {CORPUS_OUT.name} ({CORPUS_OUT.stat().st_size // 1024} Ko, {len(tokens):,} tokens)")

    if all_words:
        save_dict(all_words, "globalvoices")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=50,
                        help="Nombre de pages d'archive à parcourir")
    args = parser.parse_args()
    collect(args.pages)
