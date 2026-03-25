import re
import json
from pathlib import Path
from rapidfuzz import process, fuzz, distance


class SpellChecker:
    def __init__(self, lemmatizer):
        self.lemmatizer = lemmatizer
        base_dir = Path(__file__).resolve().parent.parent.parent  # backend/
        data_path = base_dir.parent / "data" / "corpus" / "dictionary.json"
        if not data_path.exists():
            data_path = base_dir / "data" / "corpus" / "dictionary.json"

        print(f"DEBUG SpellChecker : chargement de {data_path}")

        with open(data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Set pour is_correct O(1) ; liste triée pour rapidfuzz (stable)
        self.dictionary_set = set(
            w.lower() for w in raw
            if isinstance(w, str) and len(w) >= 3
        )
        self.dictionary_list = sorted(self.dictionary_set)

        # Combinaisons de consonnes interdites en Malagasy
        self.forbidden_patterns = re.compile(r'nb|mk|nk|dt|bp|sz', re.IGNORECASE)

    # ------------------------------------------------------------------

    def check_phonotactics(self, word: str) -> bool:
        """Vérifie les combinaisons de lettres interdites."""
        return not bool(self.forbidden_patterns.search(word))

    def is_correct(self, word: str) -> bool:
        """Mot valide = phonotactique OK ET (mot ou racine) présent dans le dictionnaire."""
        word = word.lower().strip()
        if not self.check_phonotactics(word):
            return False
        root = self.lemmatizer.get_root(word)
        return word in self.dictionary_set or root in self.dictionary_set

    def get_suggestions(self, word: str, limit: int = 5) -> list:
        """
        Corrections par distance de Levenshtein normalisée (rapidfuzz).

        Stratégie en deux passes :
        1. Levenshtein normalisé (plus précis pour les fautes de frappe courtes)
        2. Jaro-Winkler en fallback si Levenshtein ne trouve rien avec un score > seuil
           (meilleur pour les préfixes partiellement tapés)
        """
        word = word.lower().strip()

        # Passe 1 : Levenshtein normalisé — score 0→100, on garde >= 60
        lev_results = process.extract(
            word,
            self.dictionary_list,
            scorer=fuzz.ratio,
            limit=limit * 3,         # on surcharge pour filtrer ensuite
            score_cutoff=55,
        )
        suggestions = [match for match, score, _ in lev_results if score >= 55]

        # Passe 2 : Jaro-Winkler si résultats insuffisants (bon pour préfixes)
        if len(suggestions) < limit:
            jw_results = process.extract(
                word,
                self.dictionary_list,
                scorer=fuzz.token_sort_ratio,
                limit=limit * 2,
                score_cutoff=50,
            )
            for match, score, _ in jw_results:
                if match not in suggestions:
                    suggestions.append(match)

        # Re-trier par distance Levenshtein exacte (nombre d'éditions) pour précision finale
        suggestions = sorted(
            suggestions[:limit * 2],
            key=lambda w: distance.Levenshtein.distance(word, w),
        )
        return suggestions[:limit]