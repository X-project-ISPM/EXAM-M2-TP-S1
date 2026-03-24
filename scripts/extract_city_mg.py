import json
import csv

# Configuration des fichiers
input_csv = '../data/ville.csv'
output_json = '../data/tanana_mg.json'

def generate_locations_json(source, destination):
    try:
        # 1. Utilisation d'un set pour garantir l'unicité (pas de doublons)
        unique_locations = set()

        with open(source, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            
            for row in reader:
                name = row.get('fokontany', '').strip()
                
                if name and name.lower() != "unknown name" and name != "\\N":
                    unique_locations.add(name)
        
        # 2. Tri alphabétique pour un dataset propre
        sorted_locations = sorted(list(unique_locations))
        
        # 3. Formatage pour le NLP (Label LOC = Location)
        entities = []
        for loc in sorted_locations:
            entities.append({
                "text": loc,
                "label": "LOC"
            })
            
        # 4. Structure du dictionnaire final
        data = {
            "dataset_info": {
                "language": "mg",
                "entity_type": "Location Names (Fokontany)",
                "count": len(entities)
            },
            "entities": entities
        }
        
        # 5. Écriture du fichier JSON
        with open(destination, 'w', encoding='utf-8') as json_f:
            json.dump(data, json_f, ensure_ascii=False, indent=4)
            
        print(f"--- Succès ---")
        print(f"Fichier généré : {destination}")
        print(f"Nombre de lieux uniques (sans doublons) : {len(entities)}")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{source}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

# Lancement du script
if __name__ == "__main__":
    generate_locations_json(input_csv, output_json)