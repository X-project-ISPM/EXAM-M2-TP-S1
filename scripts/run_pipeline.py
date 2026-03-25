"""
run_pipeline.py
===============
Orchestrateur : exécute tous les scripts de collecte + nettoyage en séquence.

Étapes :
  1. Réinitialise data/corpus/dictionary.json (tableau vide)
  2. scrape_bible.py          — vocabulaire Bible malagasy
  3. scrape_wiki.py           — vocabulaire + corpus Wikipedia MG
  4. scrape_jw.py             — vocabulaire JW.org
  5. scrape_tenygasy.py       — vocabulaire tenymalagasy.org
  6. extract_roots.py         — racines morphologiques
  7. build_dictionary.py      — nettoyage final + copie backend

Usage :
  py scripts/run_pipeline.py             # pipeline complet
  py scripts/run_pipeline.py --no-scrape # seulement extract + build
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT = ROOT / "data" / "corpus" / "dictionary.json"
SCRIPTS_DIR = Path(__file__).resolve().parent

# Ordre d'exécution
SCRAPE_SCRIPTS = [
    "scrape_bible.py",
    "scrape_wiki.py",
    "scrape_jw.py",
    "scrape_tenygasy.py",
    "scrape_globalvoices.py",
    "scrape_wiktionary.py",
    "scrape_rfi.py",
]

POST_SCRIPTS = [
    "extract_roots.py",
    "build_dictionary.py",
]


def run_script(name: str) -> bool:
    path = SCRIPTS_DIR / name
    if not path.exists():
        print(f"  SKIP (introuvable) : {name}")
        return False

    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}\n")

    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print(f"\n  ERREUR (code {result.returncode}) : {name}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Pipeline de données malagasy")
    parser.add_argument("--no-scrape", action="store_true",
                        help="Sauter le scraping, ne lancer que extract + build")
    args = parser.parse_args()

    t0 = time.time()

    # 1. Réinitialiser le dictionnaire
    if not args.no_scrape:
        print("Réinitialisation de dictionary.json...")
        DICT.parent.mkdir(parents=True, exist_ok=True)
        with open(DICT, "w", encoding="utf-8") as f:
            json.dump([], f)
        print("  → fichier vidé\n")

    # 2. Scraping
    scripts = [] if args.no_scrape else SCRAPE_SCRIPTS
    scripts += POST_SCRIPTS

    ok, fail = 0, 0
    for name in scripts:
        if run_script(name):
            ok += 1
        else:
            fail += 1

    # 3. Résumé
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  PIPELINE TERMINÉ")
    print(f"  Scripts OK : {ok}  |  Échecs : {fail}")
    print(f"  Durée      : {elapsed:.0f}s")

    # Charger le résultat final
    if DICT.exists():
        with open(DICT, "r", encoding="utf-8") as f:
            final = json.load(f)
        print(f"  Dictionnaire final : {len(final)} mots")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
