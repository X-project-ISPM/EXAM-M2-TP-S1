# Documentation de l'API Autocomplete

Adress IP : 192.168.1.120
Ce point de terminaison fournit des suggestions intelligentes basées sur la saisie textuelle. Il combine la correction orthographique (Spell Checking) et la prédiction de mots (N-gram).

## 🚀 Endpoint : Autocomplete

**URL** : `/autocomplete`  
**Méthode** : `GET`  
**Description** : Analyse le texte envoyé pour soit corriger le dernier mot mal orthographié, soit prédire les mots suivants probables.

### 📥 Paramètres de requête (Query Params)

| Paramètre | Type     | Requis | Description                                       |
| :-------- | :------- | :----- | :------------------------------------------------ |
| `text`    | `string` | Oui    | La chaîne de caractères saisie par l'utilisateur. |

---

### 📤 Réponses (Responses)

#### 1. Cas de Prédiction (Succès)

Si le dernier mot est correctement orthographié, l'API suggère les mots suivants les plus probables.

- **Code** : `200 OK`
- **Contenu** :

```json
{
  "suggestions": ["fitiavana", "fotsiny", "feno"],
  "type": "prediction"
}

. Cas de Correction (Erreur d'orthographe)

Si le dernier mot est inconnu ou mal orthographié, l'API propose des corrections pour ce mot spécifique.

    Code : 200 OK

    Contenu :

JSON

{
  "error": "Mot mal orthographié",
  "suggestions": ["fitia", "fito"],
  "type": "correction"
}

3. Cas de Texte Vide

Si le texte envoyé ne contient aucun mot exploitable après nettoyage.

    Code : 200 OK

    Contenu :

JSON

{
  "suggestions": []
}
```
