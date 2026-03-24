import json
from pathlib import Path

class Lemmatizer:
    def __init__(self):
        # Configuration des chemins selon votre structure 
        base_dir = Path(__file__).resolve().parent
        data_path = (base_dir / "../../../data/corpus/dictionary.json").resolve()

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                self.roots = set(json.load(f))
        except FileNotFoundError:
            self.roots = set() # Évite le crash si le dico est vide au début

        # Préfixes officiels du Malagasy [cite: 53]
        self.prefixes = ['mi', 'ma', 'man', 'mam', 'maha', 'mpan', 'mpam', 'fi', 'fan', 'fam']
        
        # Table de mutation pour inverser les transformations morphologiques [cite: 18]
        self.mutation_table = {
            'n': ['s', 't', 'd'],
            'm': ['p', 'b'],
            'ng': ['h', 'k']
        }

    def get_root(self, word: str):
        word = word.lower().strip()
        
        if word in self.roots:
            return word
        
        for pref in self.prefixes:
            if word.startswith(pref):
                rest = word[len(pref):]
                
                # Cas 1: Retrait simple du préfixe
                if rest in self.roots:
                    return rest
                
                # Cas 2: Gestion de la mutation consonantique [cite: 17]
                if rest and rest[0] in self.mutation_table:
                    first_letter = rest[0]
                    for possible_origin in self.mutation_table[first_letter]:
                        potential_root = possible_origin + rest[1:]
                        if potential_root in self.roots:
                            return potential_root
                            
        return word