from fastapi import FastAPI
from app.modules.lemmatizer import Lemmatizer
from app.modules.spell_checker import SpellChecker

app = FastAPI(title="Malagasy Editor IA API")
lemmatizer = Lemmatizer()

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

# Initialisation des modules
lem_module = Lemmatizer()
spell_module = SpellChecker(lemmatizer=lem_module)

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