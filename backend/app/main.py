from fastapi import FastAPI
from app.modules.lemmatizer import Lemmatizer
from app.modules.spell_checker import SpellChecker
from app.modules.ngram_model import NGramModel

# Initialisation des modules
app = FastAPI(title="Malagasy Editor IA API")
lem_module = Lemmatizer()
spell_module = SpellChecker(lemmatizer=lem_module)
ngram_module = NGramModel()


@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de l'Éditeur Malagasy"}

@app.get("/lemmatize/{word}")
def lemmatize_word(word: str):
    root = lemmatizer.get_root(word)
    return {
        "original": word,
        "root": root,
        "is_root": word.lower() == root.lower()
    }

@app.get("/check")
async def check_word(word: str):
    is_valid = spell_module.is_correct(word)
    suggestions = []
    
    if not is_valid:
        suggestions = spell_module.get_suggestions(word)
        
    return {
        "word": word,
        "is_correct": is_valid,
        "suggestions": suggestions,
        "phonotactic_error": not spell_module.check_phonotactics(word)
    }

@app.get("/autocomplete")
async def autocomplete(text: str):
    # 1. NETTOYAGE : Extraire les mots
    words = ngram_module.clean_text(text)
    if not words:
        return {"suggestions": []}

    last_word = words[-1]

    # 2. VÉRIFICATION (Spell Checker)
    # Si le dernier mot est mal écrit (ex: "fiti"), on ne peut pas prédire la suite !
    if not spell_module.is_correct(last_word):
        # On peut soit arrêter, soit proposer des corrections pour "fiti" -> "fitia"
        corrections = spell_module.get_suggestions(last_word)
        return {
            "error": "Mot mal orthographié",
            "suggestions": corrections, # Ici on suggère des corrections d'orthographe
            "type": "correction"
        }

    # 3. ANALYSE (Lemmatizer) - Optionnel mais puissant
    # On pourrait transformer "manoratra" en "soratra" pour que le N-gram 
    # travaille sur des racines, ce qui demande un N-gram entraîné sur des racines.
    
    # 4. PRÉDICTION (N-gram)
    # Si le mot est correct, on prédit le MOT SUIVANT
    next_word_predictions = ngram_module.predict(text)
    
    return {
        "suggestions": next_word_predictions,
        "type": "prediction"
    }