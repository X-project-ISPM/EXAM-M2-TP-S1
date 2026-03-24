from fastapi import FastAPI
from app.modules.lemmatizer import Lemmatizer
from app.modules.spell_checker import SpellChecker
from app.modules.ngram_model import NGramModel
from fastapi.middleware.cors import CORSMiddleware

# Initialisation des modules
app = FastAPI(title="Malagasy Editor IA API")
lem_module = Lemmatizer()
spell_module = SpellChecker(lemmatizer=lem_module)
ngram_module = NGramModel()


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/analyze/{word}")
async def analyze_word_details(word: str):
    """
    Endpoint appelé lors d'un clic droit ou d'une sélection de mot.
    Retourne la racine, la validité et des métadonnées.
    """
    root = lem_module.get_root(word)
    is_valid = spell_module.is_correct(word)
    is_phonotactic_ok = spell_module.check_phonotactics(word)
    
    # Analyse de la structure (astuce pour les points de 'Qualité IA')
    structure = "Inconnue"
    if word.startswith(tuple(lem_module.prefixes)):
        structure = "Mot dérivé (Préfixé)"
    elif word == root:
        structure = "Racine pure"

    return {
        "word": word,
        "root": root,
        "is_valid": is_valid,
        "phonotactic_ok": is_phonotactic_ok,
        "analysis": {
            "structure": structure,
            "length": len(word),
            "prefix_detected": next((p for p in lem_module.prefixes if word.startswith(p)), None)
        }
    }

@app.get("/autocomplete")
async def autocomplete(text: str):
    words = ngram_module.clean_text(text)
    if not words:
        return {"suggestions": []}

    last_word = words[-1]
    print(f"DEBUG Autocomplete : input='{text}', last_word='{last_word}'")
    # 1. Vérification orthographique
    if not spell_module.is_correct(last_word):
        corrections = spell_module.get_suggestions(last_word)
        return {
            "type": "correction",
            "suggestions": corrections
        }

    # 2. Normalisation par Lemmatisation (Optionnel mais recommandé)
    # si le mot exact n'est pas dans ses stats mais que la racine l'est.
    root = lem_module.get_root(last_word)
    
    # 3. Prédiction du mot suivant
    # On passe le texte original au N-gram qui gère déjà sa propre logique
    next_word_predictions = ngram_module.predict(text)
    
    return {
        "type": "prediction",
        "suggestions": next_word_predictions,
        "root_detected": root if root != last_word else None
    }