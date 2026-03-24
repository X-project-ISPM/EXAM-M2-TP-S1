import re
from pathlib import Path
from collections import defaultdict

class NGramModel:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        # Corpus recommandé : Wikipedia ou Bible [cite: 19, 45]
        self.corpus_path = (base_dir / "../../../data/corpus/bible_mg.txt").resolve()
        self.trigram_model = defaultdict(list)
        self.bigram_model = defaultdict(list)
        self.train()

    def clean_text(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def train(self):
        try:
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                words = self.clean_text(f.read())
            
            for i in range(len(words) - 1):
                # Bigramme : mot A -> mot B
                self.bigram_model[words[i]].append(words[i+1])
                
                # Trigramme : (mot A, mot B) -> mot C
                if i < len(words) - 2:
                    context = (words[i], words[i+1])
                    self.trigram_model[context].append(words[i+2])
        except FileNotFoundError:
            print("Corpus introuvable. L'autocomplétion sera vide.")

    def predict(self, text_input, limit=3):
        words = self.clean_text(text_input)
        if not words:
            return []

        # Stratégie 1 : Essayer le Trigramme (plus précis)
        if len(words) >= 2:
            context = (words[-2], words[-1])
            predictions = self.trigram_model.get(context, [])
            if predictions:
                return self._get_top_suggestions(predictions, limit)

        # Stratégie 2 : Repli sur le Bigramme (Backoff)
        last_word = words[-1]
        predictions = self.bigram_model.get(last_word, [])
        return self._get_top_suggestions(predictions, limit)

    def _get_top_suggestions(self, raw_list, limit):
        # Compte les fréquences pour suggérer les mots les plus probables
        counts = {}
        for w in raw_list:
            counts[w] = counts.get(w, 0) + 1
        sorted_p = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_p[:limit]]