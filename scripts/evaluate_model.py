"""
evaluate_model.py
=================
Évaluation du modèle n-gram (bigramme / trigramme) avec split train/test 80/20.

Métriques calculées :
  - Perplexité (bigram + trigram)
  - Accuracy Top-1 / Top-5 (le mot réel est-il dans les K premières prédictions ?)
  - Matrice de confusion sur les prédictions (correct / incorrect / no-prediction)
  - Précision, Rappel, F1-score

Usage :
  py scripts/evaluate_model.py
"""

import re
import random
import math
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
CORPUS_FILES = [
    ROOT / "data" / "corpus" / "bible_mg.txt",
    ROOT / "data" / "corpus" / "wiki_mg.txt",
    ROOT / "data" / "corpus" / "jw_mg.txt",
    ROOT / "data" / "corpus" / "globalvoices_mg.txt",
    ROOT / "data" / "corpus" / "wiktionary_mg.txt",
    ROOT / "data" / "corpus" / "rfi_mg.txt",
]

TRAIN_RATIO = 0.8
SEED = 42
TOP_K_VALUES = [1, 3, 5]
MAX_TOKENS_PER_CORPUS = 300_000  # Plafond pour équilibrer les sources
MAX_TEST_TOKENS = 50_000  # Plafond du test pour vitesse d'évaluation

# Lissage Kneser-Ney
KN_DISCOUNT = 0.75
MAX_CANDIDATES = 150  # Cap pour la rapidité


# ---------------------------------------------------------------------------
# Tokenisation
# ---------------------------------------------------------------------------

def clean_text(text: str) -> list:
    return re.findall(r'\b[a-zA-ZÀ-öø-ÿ]+\b', text.lower())


# ---------------------------------------------------------------------------
# Entraînement n-gram
# ---------------------------------------------------------------------------

def train_ngram(words: list):
    bigram: dict[str, Counter] = {}
    trigram: dict[tuple, Counter] = {}
    fourgram: dict[tuple, Counter] = {}
    unigram: Counter = Counter(words)

    for i in range(len(words) - 1):
        w, nxt = words[i], words[i + 1]
        if w not in bigram:
            bigram[w] = Counter()
        bigram[w][nxt] += 1

        if i < len(words) - 2:
            ctx = (w, nxt)
            if ctx not in trigram:
                trigram[ctx] = Counter()
            trigram[ctx][words[i + 2]] += 1

            if i < len(words) - 3:
                ctx4 = (w, nxt, words[i + 2])
                if ctx4 not in fourgram:
                    fourgram[ctx4] = Counter()
                fourgram[ctx4][words[i + 3]] += 1

    # Kneser-Ney : continuation_count[w] = nb de contextes gauches uniques pour w
    continuation_count: Counter = Counter()
    for v, counter in bigram.items():
        for w in counter:
            continuation_count[w] += 1
    total_bigram_types = sum(len(c) for c in bigram.values())

    vocab = sorted(set(words))
    return bigram, trigram, fourgram, unigram, continuation_count, total_bigram_types, vocab


# ---------------------------------------------------------------------------
# Métriques
# ---------------------------------------------------------------------------

def compute_perplexity_bigram(bigram, test_words, vocab_size):
    """Perplexité bigramme avec lissage de Laplace (+1)."""
    log_prob_sum = 0.0
    n = 0
    for i in range(len(test_words) - 1):
        w, nxt = test_words[i], test_words[i + 1]
        counter = bigram.get(w, Counter())
        count_w_nxt = counter.get(nxt, 0)
        count_w = sum(counter.values()) if counter else 0
        # Lissage de Laplace
        prob = (count_w_nxt + 1) / (count_w + vocab_size)
        log_prob_sum += math.log2(prob)
        n += 1
    if n == 0:
        return float('inf')
    return 2 ** (-log_prob_sum / n)


def compute_perplexity_trigram(trigram, bigram, test_words, vocab_size):
    """Perplexité trigramme avec backoff bigramme + Laplace."""
    log_prob_sum = 0.0
    n = 0
    for i in range(len(test_words) - 2):
        w1, w2, w3 = test_words[i], test_words[i + 1], test_words[i + 2]
        ctx = (w1, w2)
        if ctx in trigram:
            counter = trigram[ctx]
            count_ctx_w3 = counter.get(w3, 0)
            count_ctx = sum(counter.values())
            prob = (count_ctx_w3 + 1) / (count_ctx + vocab_size)
        else:
            # Backoff vers bigramme
            counter = bigram.get(w2, Counter())
            count_w2_w3 = counter.get(w3, 0)
            count_w2 = sum(counter.values()) if counter else 0
            prob = (count_w2_w3 + 1) / (count_w2 + vocab_size)
        log_prob_sum += math.log2(prob)
        n += 1
    if n == 0:
        return float('inf')
    return 2 ** (-log_prob_sum / n)


def predict_next(bigram, trigram, fourgram, continuation_count, total_bigram_types, words, limit=5):
    """Prédit les K prochains mots avec Kneser-Ney (bi/tri/4-gramme)."""
    if not words:
        return []
    last = words[-1]
    prev = words[-2] if len(words) >= 2 else None
    prev2 = words[-3] if len(words) >= 3 else None

    # Collecter les candidats (limités pour performance)
    candidates: set = set()
    if prev2 and prev:
        ctx4 = (prev2, prev, last)
        if ctx4 in fourgram:
            candidates.update(w for w, _ in fourgram[ctx4].most_common(MAX_CANDIDATES))
    if prev:
        ctx = (prev, last)
        if ctx in trigram:
            candidates.update(w for w, _ in trigram[ctx].most_common(MAX_CANDIDATES))
    if last in bigram:
        candidates.update(w for w, _ in bigram[last].most_common(MAX_CANDIDATES))

    if not candidates:
        # Fallback : mots les plus courants par continuation count (mots OOV)
        return [w for w, _ in continuation_count.most_common(limit)]

    # Scorer par Kneser-Ney hiérarchique
    D = KN_DISCOUNT
    total_bt = max(total_bigram_types, 1)

    bi_counter = bigram.get(last, Counter())
    bi_total = sum(bi_counter.values()) if bi_counter else 0
    n_bi_types = len(bi_counter)

    tri_counter = trigram.get((prev, last), Counter()) if prev else Counter()
    tri_total = sum(tri_counter.values()) if tri_counter else 0
    n_tri_types = len(tri_counter)

    four_counter = fourgram.get((prev2, prev, last), Counter()) if (prev2 and prev) else Counter()
    four_total = sum(four_counter.values()) if four_counter else 0
    n_four_types = len(four_counter)

    scores = {}
    for w in candidates:
        # KN unigramme : probabilité de continuation
        p_kn_uni = continuation_count.get(w, 0) / total_bt

        # KN bigramme
        if bi_total > 0:
            lambda_bi = D * n_bi_types / bi_total
            p_kn_bi = max(bi_counter.get(w, 0) - D, 0.0) / bi_total + lambda_bi * p_kn_uni
        else:
            p_kn_bi = p_kn_uni

        # KN trigramme
        if tri_total > 0 and prev:
            lambda_tri = D * n_tri_types / tri_total
            p_kn_tri = max(tri_counter.get(w, 0) - D, 0.0) / tri_total + lambda_tri * p_kn_bi
        else:
            p_kn_tri = p_kn_bi

        # KN 4-gramme
        if four_total > 0 and prev2 and prev:
            lambda_four = D * n_four_types / four_total
            p_kn = max(four_counter.get(w, 0) - D, 0.0) / four_total + lambda_four * p_kn_tri
        else:
            p_kn = p_kn_tri

        scores[w] = p_kn

    ranked = sorted(scores, key=scores.get, reverse=True)
    return ranked[:limit]


def evaluate_topk(bigram, trigram, fourgram, continuation_count, total_bigram_types, test_words, top_k_values):
    """
    Pour chaque position dans le test, on prédit le mot suivant.
    On mesure si le vrai mot est dans le top-K.
    
    Retourne aussi la matrice de confusion 3 classes :
      - CORRECT   : prédiction top-1 = mot réel
      - IN_TOP_K  : mot réel dans top-K mais pas top-1
      - WRONG     : prédiction faite mais mot réel absent du top-K
      - NO_PRED   : aucune prédiction possible
    """
    max_k = max(top_k_values)
    hits = {k: 0 for k in top_k_values}
    total = 0
    confusion = {"correct": 0, "in_top_k": 0, "wrong": 0, "no_pred": 0}

    for i in range(1, len(test_words) - 1):
        context = test_words[max(0, i - 1): i + 1]
        if len(context) < 1:
            continue
        actual = test_words[i + 1]
        preds = predict_next(bigram, trigram, fourgram, continuation_count, total_bigram_types, context, limit=max_k)
        total += 1

        if not preds:
            confusion["no_pred"] += 1
            continue

        for k in top_k_values:
            if actual in preds[:k]:
                hits[k] += 1

        if preds[0] == actual:
            confusion["correct"] += 1
        elif actual in preds[:max_k]:
            confusion["in_top_k"] += 1
        else:
            confusion["wrong"] += 1

    accuracy = {k: hits[k] / total * 100 if total else 0 for k in top_k_values}
    return accuracy, confusion, total


# ---------------------------------------------------------------------------
# Affichage
# ---------------------------------------------------------------------------

def print_separator(title=""):
    print(f"\n{'='*60}")
    if title:
        print(f"  {title}")
        print(f"{'='*60}")


def print_confusion_matrix(confusion, total):
    """Affiche la matrice de confusion en format tableau."""
    print("\n┌──────────────────┬──────────┬────────────┐")
    print("│ Catégorie        │  Nombre  │ Proportion │")
    print("├──────────────────┼──────────┼────────────┤")
    for label, count in confusion.items():
        pct = count / total * 100 if total else 0
        name = {
            "correct": "✓ Correct (top-1)",
            "in_top_k": "~ Dans top-K",
            "wrong": "✗ Mauvais",
            "no_pred": "⊘ Pas de préd.",
        }[label]
        print(f"│ {name:<16} │ {count:>8} │ {pct:>9.2f}% │")
    print("├──────────────────┼──────────┼────────────┤")
    print(f"│ {'TOTAL':<16} │ {total:>8} │ {'100.00%':>10} │")
    print("└──────────────────┴──────────┴────────────┘")


def print_classification_report(confusion, total):
    """Précision, Rappel, F1 pour la classe 'correct' (top-1)."""
    tp = confusion["correct"]
    fp = confusion["wrong"]     # prédit mais faux
    fn = confusion["in_top_k"] + confusion["no_pred"]  # pas top-1

    precision = tp / (tp + fp) * 100 if (tp + fp) else 0
    recall = tp / (tp + fn) * 100 if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0

    print("\n┌─────────────┬──────────┐")
    print("│ Métrique    │  Score   │")
    print("├─────────────┼──────────┤")
    print(f"│ Précision   │ {precision:>7.2f}% │")
    print(f"│ Rappel      │ {recall:>7.2f}% │")
    print(f"│ F1-Score    │ {f1:>7.2f}% │")
    print("└─────────────┴──────────┘")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print_separator("ÉVALUATION DU MODÈLE N-GRAM MALAGASY")
    print(f"  Split : {TRAIN_RATIO*100:.0f}% train / {(1-TRAIN_RATIO)*100:.0f}% test")
    print(f"  Seed  : {SEED}")

    # 1. Charger tous les corpus (avec balancing)
    all_words = []
    for path in CORPUS_FILES:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            words = clean_text(text)
            original = len(words)
            if len(words) > MAX_TOKENS_PER_CORPUS:
                words = words[:MAX_TOKENS_PER_CORPUS]
            all_words.extend(words)
            cap = f" (plafonné à {len(words):,})" if len(words) < original else ""
            print(f"  Corpus : {path.name} → {original:,} tokens{cap}")
        else:
            print(f"  SKIP   : {path.name} (introuvable)")

    if not all_words:
        print("ERREUR : aucun corpus trouvé !")
        return

    print(f"\n  Total tokens : {len(all_words):,}")
    print(f"  Vocabulaire  : {len(set(all_words)):,} mots uniques")

    # 2. Split 80/20 (par phrases = séquences continues)
    # On découpe en blocs de 50 mots pour simuler des "phrases"
    BLOCK_SIZE = 50
    blocks = [all_words[i:i+BLOCK_SIZE] for i in range(0, len(all_words), BLOCK_SIZE)]
    random.seed(SEED)
    random.shuffle(blocks)

    split_idx = int(len(blocks) * TRAIN_RATIO)
    train_blocks = blocks[:split_idx]
    test_blocks = blocks[split_idx:]

    train_words = [w for block in train_blocks for w in block]
    test_words = [w for block in test_blocks for w in block]
    test_words = test_words[:MAX_TEST_TOKENS]

    print(f"\n  Train : {len(train_words):,} tokens ({len(train_blocks)} blocs)")
    print(f"  Test  : {len(test_words):,} tokens (plafonné à {MAX_TEST_TOKENS:,} pour vitesse)")

    # 3. Entraîner sur le train set
    print_separator("ENTRAÎNEMENT (sur 80% des données)")
    bigram, trigram, fourgram, unigram, continuation_count, total_bigram_types, vocab = train_ngram(train_words)
    vocab_size = len(vocab)
    print(f"  Vocabulaire entraîné : {vocab_size:,} mots")
    print(f"  Bigrammes uniques    : {sum(len(c) for c in bigram.values()):,}")
    print(f"  Trigrammes uniques   : {sum(len(c) for c in trigram.values()):,}")
    print(f"  4-grammes uniques    : {sum(len(c) for c in fourgram.values()):,}")

    # 4. Perplexité
    print_separator("PERPLEXITÉ (sur 20% test)")
    ppl_bi = compute_perplexity_bigram(bigram, test_words, vocab_size)
    ppl_tri = compute_perplexity_trigram(trigram, bigram, test_words, vocab_size)
    print(f"  Perplexité bigramme  : {ppl_bi:,.2f}")
    print(f"  Perplexité trigramme : {ppl_tri:,.2f}")
    print(f"  (plus bas = meilleur ; ~100-500 typique pour un n-gram)")

    # 5. Top-K Accuracy
    print_separator("ACCURACY TOP-K (sur 20% test)")
    accuracy, confusion, total = evaluate_topk(bigram, trigram, fourgram, continuation_count, total_bigram_types, test_words, TOP_K_VALUES)
    for k in TOP_K_VALUES:
        bar = "█" * int(accuracy[k] / 2) + "░" * (50 - int(accuracy[k] / 2))
        print(f"  Top-{k} : {accuracy[k]:>6.2f}%  {bar}")

    # 6. Matrice de confusion
    print_separator("MATRICE DE CONFUSION")
    print(f"  (top-K = top-{max(TOP_K_VALUES)})")
    print_confusion_matrix(confusion, total)

    # 7. Classification Report
    print_separator("RAPPORT DE CLASSIFICATION (top-1)")
    print_classification_report(confusion, total)

    # 8. Exemples de prédictions
    print_separator("EXEMPLES DE PRÉDICTIONS (10 premiers du test)")
    for i in range(min(10, len(test_words) - 2)):
        ctx = test_words[i:i+2]
        actual = test_words[i + 2]
        preds = predict_next(bigram, trigram, fourgram, continuation_count, total_bigram_types, ctx, limit=5)
        hit = "✓" if actual in preds else "✗"
        print(f"  {hit} \"{ctx[0]} {ctx[1]}\" → vrai: {actual:<15} prédit: {preds[:3]}")

    print_separator("FIN DE L'ÉVALUATION")


if __name__ == "__main__":
    main()
