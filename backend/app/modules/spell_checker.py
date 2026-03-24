import re
import json
from pathlib import Path
from rapidfuzz import process, utils

class SpellChecker:
    def __init__(self, lemmatizer):
        self.lemmatizer = lemmatizer
        base_dir = Path(__file__).resolve().parent
       # On remonte de : modules -> app -> backend (2 niveaux suffisent généralement)
        # Mais pour être sûr, on cherche le dossier 'data' à partir de la racine backend
        base_dir = Path(__file__).resolve().parent.parent.parent # Remonte à 'backend/'
        data_path = base_dir / "data" / "corpus" / "dictionary.json"

        # DEBUG : Affiche le chemin calculé dans ton terminal pour vérifier
        print(f"DEBUG SpellChecker : tentative d'ouverture de {data_path}")

        with open(data_path, "r", encoding="utf-8") as f:
            # On stocke les racines pour la comparaison
            self.dictionary = json.load(f)
        
        # Combinaisons interdites selon le cahier des charges [cite: 51]
        self.forbidden_patterns = r'nb|mk|nk|dt|bp|sz'

    def check_phonotactics(self, word):
        """Vérifie les combinaisons de lettres interdites [cite: 17, 52]"""
        if re.search(self.forbidden_patterns, word.lower()):
            return False
        return True

    def is_correct(self, word):
        """Vérifie si le mot est valide (directement ou via sa racine)"""
        word = word.lower().strip()
        
        # 1. Test phonotactique
        if not self.check_phonotactics(word):
            return False
            
        # 2. Test dictionnaire (mot complet ou racine)
        root = self.lemmatizer.get_root(word)
        if word in self.dictionary or root in self.dictionary:
            return True
            
        return False

    def get_suggestions(self, word, limit=3):
        """Propose des corrections via la distance de Levenshtein """
        # On utilise rapidfuzz pour trouver les correspondances les plus proches
        suggestions = process.extract(
            word, 
            self.dictionary, 
            limit=limit,
            processor=utils.default_process
        )
        return [s[0] for s in suggestions]