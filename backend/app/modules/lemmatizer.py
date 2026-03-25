import json
from pathlib import Path


class Lemmatizer:
    def __init__(self):
        # En Docker : /app → volume ./data monté dans /app/data
        # En local  : backend/app/modules → remonte à la racine du projet
        base_dir = Path(__file__).resolve().parent.parent.parent  # backend/
        data_path = base_dir.parent / "data" / "corpus" / "dictionary.json"
        # Fallback Docker : /app/data (volume mount)
        if not data_path.exists():
            data_path = base_dir / "data" / "corpus" / "dictionary.json"

        print(f"DEBUG Lemmatizer : chargement de {data_path}")

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Filtre au chargement : mots >= 3 lettres, pas de bruit "aaa"
            self.roots = set(
                w.lower() for w in raw
                if isinstance(w, str) and len(w) >= 3 and not self._is_noise(w)
            )
        except FileNotFoundError:
            print("WARN Lemmatizer : dictionnaire introuvable, racines vides.")
            self.roots = set()

        # Préfixes du plus long au plus court pour éviter les faux positifs
        self.prefixes = [
            'mpan', 'mpam', 'maha', 'man', 'mam', 'mi', 'ma',
            'fan', 'fam', 'fi',
            'an', 'am',
        ]

        # Suffixes courants du Malagasy
        self.suffixes = ['areo', 'ana', 'ina', 'iny', 'any', 'nao', 'ko', 'ny', 'tra', 'dra']

        # Table de mutation consonantique (surface → origines possibles)
        # Ex : "man" + "banjaka" → racine "panjaka" (m←p)
        self.mutation_table = {
            'n':  ['s', 't', 'd'],
            'm':  ['p', 'b'],
            'ng': ['h', 'k'],
        }

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def _is_noise(word: str) -> bool:
        """Filtre les entrées aberrantes du dictionnaire scrappé."""
        w = word.lower()
        if len(set(w)) == 1 and len(w) > 2:   # "aaa", "eeee" …
            return True
        alpha_ratio = sum(c.isalpha() for c in w) / max(len(w), 1)
        return alpha_ratio < 0.8

    def _strip_suffix(self, word: str) -> list:
        """Retourne une liste de candidats-racines après suppression d'un suffixe."""
        candidates = []
        for suf in self.suffixes:
            if word.endswith(suf) and len(word) - len(suf) >= 3:
                candidates.append(word[: -len(suf)])
        return candidates

    # ------------------------------------------------------------------
    # API principale
    # ------------------------------------------------------------------

    def get_root(self, word: str) -> str:
        word = word.lower().strip()

        # 1. Mot déjà connu → c'est la racine
        if word in self.roots:
            return word

        # 2. Suppression de préfixe
        for pref in self.prefixes:
            if word.startswith(pref):
                rest = word[len(pref):]

                # Retrait simple
                if rest in self.roots:
                    return rest

                # Mutation consonantique — on teste 'ng' (2 chars) PUIS les mono-chars
                mutations_to_check = []
                if rest[:2] in self.mutation_table:          # 'ng'
                    mutations_to_check += [
                        (rest[:2], orig) for orig in self.mutation_table[rest[:2]]
                    ]
                if rest and rest[0] in self.mutation_table:  # 'n', 'm'
                    mutations_to_check += [
                        (rest[0], orig) for orig in self.mutation_table[rest[0]]
                    ]

                for surface, origin in mutations_to_check:
                    candidate = origin + rest[len(surface):]
                    if candidate in self.roots:
                        return candidate

                # Suffixe sur le reste après préfixe
                for candidate in self._strip_suffix(rest):
                    if candidate in self.roots:
                        return candidate

        # 3. Suppression de suffixe seul (sans préfixe)
        for candidate in self._strip_suffix(word):
            if candidate in self.roots:
                return candidate

        # 4. Inconnu → mot original
        return word