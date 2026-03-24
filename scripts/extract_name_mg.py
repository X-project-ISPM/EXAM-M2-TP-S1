import json

# Configuration des fichiers
input_txt = '../data/anarana_malagasy.txt'
output_json = '../data/anarana_mg.json'

def generate_names_json(source, destination):
    try:
        # 1. Extraction et nettoyage
        with open(source, 'r', encoding='utf-8') as f:
            names_list = [line.strip() for line in f if line.strip()]
        
        # 2. Suppression des doublons et tri alphabétique
        unique_names = sorted(list(set(names_list)))
        
        # 3. Formatage pour le NLP (Label PER = Personne)
        entities = []
        for name in unique_names:
            entities.append({
                "text": name,
                "label": "PER"
            })
            
        # 4. Structure du dictionnaire final
        data = {
            "dataset_info": {
                "language": "mg",
                "entity_type": "Personal Names",
                "count": len(entities)
            },
            "entities": entities
        }
        
        # 5. Écriture du fichier JSON
        with open(destination, 'w', encoding='utf-8') as json_f:
            json.dump(data, json_f, ensure_ascii=False, indent=4)
            
        print(f"--- Succès ---")
        print(f"Fichier généré : {destination}")
        print(f"Nombre de noms uniques : {len(entities)}")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{source}' n'a pas été trouvé.")

# Lancement du script
if __name__ == "__main__":
    generate_names_json(input_txt, output_json)