import re
import pickle
from pathlib import Path
from collections import Counter


class NGramModel:
    # Discount pour le lissage Kneser-Ney (valeur standard = 0.75)
    KN_DISCOUNT = 0.75

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent.parent  # backend/
        corpus_dir = (base_dir.parent / "data" / "corpus").resolve()
        if not corpus_dir.exists():
            corpus_dir = (base_dir / "data" / "corpus").resolve()

        # Corpus : Bible + Wikipedia + JW.org + Global Voices + Wiktionary + RFI
        self.corpus_paths = [
            corpus_dir / "bible_mg.txt",
            corpus_dir / "wiki_mg.txt",
            corpus_dir / "jw_mg.txt",
            corpus_dir / "globalvoices_mg.txt",
            corpus_dir / "wiktionary_mg.txt",
            corpus_dir / "rfi_mg.txt",
        ]

        # Plafond de tokens par corpus pour équilibrer l'entraînement
        self.max_tokens_per_corpus = 300_000

        # Cache pickle nommé d'après tous les corpus actifs
        self.cache_path = corpus_dir / "ngram_model.pkl"

        self.bigram_model: dict[str, Counter] = {}
        self.trigram_model: dict[tuple, Counter] = {}
        self.fourgram_model: dict[tuple, Counter] = {}
        self.unigram_model: Counter = Counter()
        self.total_tokens: int = 0
        # Kneser-Ney : compte de continuations et total de bigrammes distincts
        self.continuation_count: Counter = Counter()
        self.total_bigram_types: int = 0
        # Index vocabulaire pour la complétion par préfixe
        self.vocabulary: list[str] = []

        self._load_or_train()

    # ------------------------------------------------------------------
    # Entraînement / persistance
    # ------------------------------------------------------------------

    def clean_text(self, text: str) -> list:
        return re.findall(r'\b[a-zA-ZÀ-öø-ÿ]+\b', text.lower())

    def _train(self, words: list) -> None:
        bigram: dict[str, Counter] = {}
        trigram: dict[tuple, Counter] = {}
        fourgram: dict[tuple, Counter] = {}
        unigram: Counter = Counter(words)

        for i in range(len(words) - 1):
            w = words[i]
            nxt = words[i + 1]

            # Bigramme
            if w not in bigram:
                bigram[w] = Counter()
            bigram[w][nxt] += 1

            # Trigramme
            if i < len(words) - 2:
                ctx = (w, nxt)
                if ctx not in trigram:
                    trigram[ctx] = Counter()
                trigram[ctx][words[i + 2]] += 1

                # 4-gramme
                if i < len(words) - 3:
                    ctx4 = (w, nxt, words[i + 2])
                    if ctx4 not in fourgram:
                        fourgram[ctx4] = Counter()
                    fourgram[ctx4][words[i + 3]] += 1

        # Kneser-Ney : continuation counts
        # continuation_count[w] = nombre de contextes gauches uniques pour w
        continuation_count: Counter = Counter()
        for v, counter in bigram.items():
            for w in counter:
                continuation_count[w] += 1

        self.bigram_model = bigram
        self.trigram_model = trigram
        self.fourgram_model = fourgram
        self.unigram_model = unigram
        self.total_tokens = len(words)
        self.continuation_count = continuation_count
        self.total_bigram_types = sum(len(c) for c in bigram.values())
        self.vocabulary = sorted(set(words))

    def _load_or_train(self) -> None:
        """Charge le modèle depuis le cache pickle ; entraîne si absent ou obsolète."""
        # Le cache est valide tant qu'aucun corpus source n'est plus récent
        if self.cache_path.exists():
            cache_mtime = self.cache_path.stat().st_mtime
            corpus_mtimes = [
                p.stat().st_mtime for p in self.corpus_paths if p.exists()
            ]
            if corpus_mtimes and cache_mtime >= max(corpus_mtimes):
                try:
                    with open(self.cache_path, "rb") as f:
                        data = pickle.load(f)
                    self.bigram_model = data["bigram"]
                    self.trigram_model = data["trigram"]
                    self.fourgram_model = data.get("fourgram", {})
                    self.unigram_model = data.get("unigram", Counter())
                    self.total_tokens = data.get("total_tokens", sum(self.unigram_model.values()))
                    self.continuation_count = data.get("continuation_count", Counter())
                    self.total_bigram_types = data.get("total_bigram_types", sum(len(c) for c in self.bigram_model.values()))
                    self.vocabulary = data["vocab"]
                    print(f"NGramModel : modèle chargé depuis cache ({len(self.vocabulary)} mots)")
                    return
                except Exception:
                    pass  # cache corrompu → ré-entraîner

        # Entraînement sur tous les corpus disponibles (avec balancing)
        all_words: list[str] = []
        for path in self.corpus_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    words = self.clean_text(f.read())
                original_len = len(words)
                # Plafonner les gros corpus pour équilibrer
                if len(words) > self.max_tokens_per_corpus:
                    words = words[:self.max_tokens_per_corpus]
                all_words.extend(words)
                cap_info = f" (plafonné à {len(words):,})" if len(words) < original_len else ""
                print(f"NGramModel : corpus '{path.name}' → {original_len:,} tokens{cap_info}")

        if not all_words:
            print("WARN NGramModel : aucun corpus trouvé, autocomplétion désactivée.")
            return

        print(f"NGramModel : entraînement sur {len(all_words)} tokens au total…")
        self._train(all_words)
        with open(self.cache_path, "wb") as f:
            pickle.dump({"bigram": self.bigram_model,
                         "trigram": self.trigram_model,
                         "fourgram": self.fourgram_model,
                         "unigram": self.unigram_model,
                         "total_tokens": self.total_tokens,
                         "continuation_count": self.continuation_count,
                         "total_bigram_types": self.total_bigram_types,
                         "vocab": self.vocabulary}, f)
        print("NGramModel : cache pickle sauvegardé.")

    # ------------------------------------------------------------------
    # Prédiction
    # ------------------------------------------------------------------

    def predict(self, text_input: str, limit: int = 5) -> list:
        words = self.clean_text(text_input)
        if not words:
            return []

        last = words[-1]
        prev = words[-2] if len(words) >= 2 else None

        # Collecter tous les candidats depuis 4-gramme, trigramme et bigramme
        candidates: set = set()
        prev2 = words[-3] if len(words) >= 3 else None

        if prev2 and prev:
            ctx4 = (prev2, prev, last)
            if ctx4 in self.fourgram_model:
                candidates.update(self.fourgram_model[ctx4].keys())
        if prev:
            ctx = (prev, last)
            if ctx in self.trigram_model:
                candidates.update(self.trigram_model[ctx].keys())
        if last in self.bigram_model:
            candidates.update(self.bigram_model[last].keys())

        if not candidates:
            # Fallback KN-unigramme : mots les plus courants par continuation count
            return [w for w, _ in self.continuation_count.most_common(limit)] or self._prefix_complete(last, limit)

        # Scorer chaque candidat par lissage Kneser-Ney hiérarchique
        D = self.KN_DISCOUNT
        total_bt = max(self.total_bigram_types, 1)

        bi_counter = self.bigram_model.get(last, Counter())
        bi_total = sum(bi_counter.values()) if bi_counter else 0
        n_bi_types = len(bi_counter)

        tri_counter = self.trigram_model.get((prev, last), Counter()) if prev else Counter()
        tri_total = sum(tri_counter.values()) if tri_counter else 0
        n_tri_types = len(tri_counter)

        four_counter = self.fourgram_model.get((prev2, prev, last), Counter()) if (prev2 and prev) else Counter()
        four_total = sum(four_counter.values()) if four_counter else 0
        n_four_types = len(four_counter)

        scores: dict[str, float] = {}
        for w in candidates:
            # KN unigramme : probabilité de continuation
            p_kn_uni = self.continuation_count.get(w, 0) / total_bt

            # KN bigramme : absolute discounting + backoff KN unigramme
            if bi_total > 0:
                lambda_bi = D * n_bi_types / bi_total
                p_kn_bi = max(bi_counter.get(w, 0) - D, 0.0) / bi_total + lambda_bi * p_kn_uni
            else:
                p_kn_bi = p_kn_uni

            # KN trigramme : absolute discounting + backoff KN bigramme
            if tri_total > 0 and prev:
                lambda_tri = D * n_tri_types / tri_total
                p_kn_tri = max(tri_counter.get(w, 0) - D, 0.0) / tri_total + lambda_tri * p_kn_bi
            else:
                p_kn_tri = p_kn_bi

            # KN 4-gramme : absolute discounting + backoff KN trigramme
            if four_total > 0 and prev2 and prev:
                lambda_four = D * n_four_types / four_total
                p_kn = max(four_counter.get(w, 0) - D, 0.0) / four_total + lambda_four * p_kn_tri
            else:
                p_kn = p_kn_tri

            scores[w] = p_kn

        ranked = sorted(scores, key=scores.get, reverse=True)
        return ranked[:limit]

    def _prefix_complete(self, prefix: str, limit: int) -> list:
        """Retourne les mots du vocabulaire commençant par `prefix`."""
        return [w for w in self.vocabulary if w.startswith(prefix) and w != prefix][:limit]
    def _get_top_suggestions(self, raw_list, limit):
        # Compte les fréquences pour suggérer les mots les plus probables
        counts = {}
        for w in raw_list:
            counts[w] = counts.get(w, 0) + 1
        sorted_p = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_p[:limit]]