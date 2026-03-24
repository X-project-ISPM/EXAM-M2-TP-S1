# API Reference — Backend Proxy

Le backend proxy tourne sur le port **8000** et expose les endpoints suivants au frontend.

> **Rate limiting global :** 60 requêtes / minute par IP.  
> **CORS :** autorisé uniquement depuis `http://localhost:3000` (ou `FRONTEND_URL`).

---

## GET `/health`

Health check du proxy.

**Réponse**
```json
{ "status": "ok", "service": "backend-proxy" }
```

---

## GET `/autocomplete`

Suggestions d'autocomplétion. Proxie vers le backend Python (`192.168.1.120`).

**Paramètres de query**

| Paramètre | Type   | Requis | Max      | Description          |
|-----------|--------|--------|----------|----------------------|
| `text`    | string | oui    | 500 car. | Texte à compléter    |

**Exemple de requête**
```
GET /autocomplete?text=mira
```

**Réponse**
```json
{
  "suggestions": ["mirary", "miranga", "miray"],
  "type": "prediction"
}
```

> `type` peut valoir `"prediction"` ou `"correction"`.  
> **Cache :** 5 minutes.

---

## POST `/api/translate`

Traduction de texte via Gemini AI.

**Body (JSON)**

| Champ  | Type   | Requis | Max      | Défaut | Description                        |
|--------|--------|--------|----------|--------|------------------------------------|
| `text` | string | oui    | 500 car. | —      | Texte à traduire                   |
| `from` | string | non    | 10 car.  | `"mg"` | Code langue source (BCP-47)        |
| `to`   | string | non    | 10 car.  | `"fr"` | Code langue cible (BCP-47)         |

**Langues supportées**

| Code | Langue   |
|------|----------|
| `mg` | Malgache |
| `fr` | Français |
| `en` | Anglais  |
| `es` | Espagnol |
| `de` | Allemand |
| `zh` | Chinois  |

**Exemple de requête**
```json
{
  "text": "Manao ahoana",
  "from": "mg",
  "to": "fr"
}
```

**Réponse**
```json
{
  "text": "Manao ahoana",
  "from": "mg",
  "to": "fr",
  "translation": "Comment allez-vous"
}
```

> **Cache :** oui (basé sur `text + from + to`).

---

## POST `/api/tts`

Synthèse vocale (Text-to-Speech) via Gemini TTS. Retourne un fichier WAV encodé en base64.

**Body (JSON)**

| Champ   | Type   | Requis | Max       | Défaut   | Description          |
|---------|--------|--------|-----------|----------|----------------------|
| `text`  | string | oui    | 1000 car. | —        | Texte à synthétiser  |
| `voice` | string | non    | 50 car.   | `"Aoede"`| Voix à utiliser      |

**Voix disponibles**

`Aoede`, `Charon`, `Fenrir`, `Kore`, `Orbit`, `Puck`, `Schedar`, `Sulafat`

**Exemple de requête**
```json
{
  "text": "Manao ahoana ry namana",
  "voice": "Kore"
}
```

**Réponse**
```json
{
  "audio": "<base64 WAV>",
  "format": "wav",
  "mimeType": "audio/wav",
  "encoding": "base64"
}
```

**Lecture côté frontend**
```js
const audio = new Audio("data:audio/wav;base64," + response.audio);
audio.play();
```

> **Cache :** 24 heures.

---

## POST `/api/ner`

Reconnaissance d'entités nommées (NER) via Gemini AI.

**Body (JSON)**

| Champ  | Type   | Requis | Max       | Description          |
|--------|--------|--------|-----------|----------------------|
| `text` | string | oui    | 2000 car. | Texte à analyser     |

**Exemple de requête**
```json
{
  "text": "Nipetraka tao Antananarivo i Rasoa"
}
```

**Réponse**
```json
{
  "text": "Nipetraka tao Antananarivo i Rasoa",
  "entities": [
    { "name": "Antananarivo", "type": "LOCATION", "salience": 0.8 },
    { "name": "Rasoa", "type": "PERSON", "salience": 0.6 }
  ]
}
```

**Types d'entités possibles**

| Type            | Description              |
|-----------------|--------------------------|
| `PERSON`        | Personne                 |
| `LOCATION`      | Lieu                     |
| `ORGANIZATION`  | Organisation             |
| `EVENT`         | Événement                |
| `WORK_OF_ART`   | Œuvre artistique         |
| `CONSUMER_GOOD` | Produit de consommation  |
| `OTHER`         | Autre                    |

> `salience` : score d'importance entre `0.0` (faible) et `1.0` (élevé).  
> **Cache :** oui.

---

## POST `/api/sentiment`

Analyse de sentiment via Gemini AI.

**Body (JSON)**

| Champ  | Type   | Requis | Max       | Description          |
|--------|--------|--------|-----------|----------------------|
| `text` | string | oui    | 2000 car. | Texte à analyser     |

**Exemple de requête**
```json
{
  "text": "Mahafaly ahy izany vaovao izany"
}
```

**Réponse**
```json
{
  "text": "Mahafaly ahy izany vaovao izany",
  "score": 0.85,
  "magnitude": 0.9,
  "label": "positif"
}
```

| Champ       | Type   | Description                                           |
|-------------|--------|-------------------------------------------------------|
| `score`     | number | De `-1.0` (très négatif) à `+1.0` (très positif)     |
| `magnitude` | number | Intensité émotionnelle globale (`0` = neutre)         |
| `label`     | string | `"positif"` / `"négatif"` / `"neutre"`               |

> Règle de label : `positif` si `score > 0.2`, `négatif` si `score < -0.2`, sinon `neutre`.  
> **Cache :** oui.

---

## POST `/api/chat`

Chatbot conversationnel spécialisé en langue malgache, via Gemini AI.

**Body (JSON)**

| Champ     | Type   | Requis | Max       | Description                              |
|-----------|--------|--------|-----------|------------------------------------------|
| `message` | string | oui    | 2000 car. | Message de l'utilisateur                 |
| `history` | array  | non    | 20 items  | Historique de la conversation (optionnel)|

**Structure de `history`**
```json
[
  { "role": "user",  "text": "C'est quoi le fokontany ?" },
  { "role": "model", "text": "Le fokontany est la plus petite division..." }
]
```

> `role` accepte : `"user"` ou `"model"`.

**Exemple de requête**
```json
{
  "message": "Ahoana ny fampiasana ny teny hoe 'mirary' ?",
  "history": []
}
```

**Réponse**
```json
{
  "reply": "Ny teny hoe 'mirary' dia midika hoe espérer ou souhaiter..."
}
```

> **Pas de cache** (conversationnel).  
> Le bot est configuré pour répondre aux questions liées à la langue malgache uniquement.

---

## Endpoints désactivés (non disponibles)

Les routes suivantes sont définies mais commentées dans le proxy. Elles ne sont pas accessibles.

| Endpoint          | Description              |
|-------------------|--------------------------|
| `/api/spellcheck` | Correction orthographique |
| `/api/lemmatize`  | Lemmatisation            |

---

## Codes d'erreur communs

| Code | Description                                              |
|------|----------------------------------------------------------|
| 400  | Validation échouée (champ manquant ou invalide)          |
| 429  | Trop de requêtes (rate limit : 60 req/min)               |
| 502  | Erreur du service externe (Gemini API)                   |
| 503  | Service indisponible (clé API manquante ou backend hors ligne) |
