# EXAM-M2-TP-S1
Thème : Éditeur de Texte Augmenté par l'IA pour le Malagasy 
# Éditeur de Texte Augmenté par l'IA pour le Malagasy

> Projet TP Machine Learning — Institut Supérieur Polytechnique de Madagascar  
> Semestre 1

---

## Membres du groupe

| Nom | Rôle |
|-----|------|
| _à compléter_ | Chef de projet / Backend |
| _à compléter_ | Frontend / UX |
| _à compléter_ | NLP / Data |
| _à compléter_ | DevOps / Intégration |

---

## Présentation du projet

Ce projet est un éditeur de texte web intelligent conçu pour assister les rédacteurs malagasy. Le Malagasy étant une langue à faibles ressources numériques (*Low Resource Language*), l'outil combine des approches symboliques, algorithmiques et data-driven pour pallier le manque de données massives. L'objectif est de proposer une expérience fluide et riche, similaire à ce que Word ou Google Docs offre pour le français ou l'anglais.

---

## Stack technique

- **Frontend** : React + Quill.js (ou TipTap) + TailwindCSS
- **Backend** : Python + FastAPI
- **Données** : JSON (dictionnaire, entités, sentiments) + `.pkl` (modèle N-gram sérialisé)
- **Déploiement** : Frontend → Vercel / Backend → Railway ou Render

---

## Structure du projet

```
malagasy-editor/
├── backend/
├── frontend/
├── data/
├── scripts/
├── README.md
├── .env.example
└── docker-compose.yml (si dockeriser)
```

---

### `backend/`

Contient toute la logique serveur de l'application. C'est ici que résident les modules d'intelligence artificielle et les endpoints API appelés par le frontend.

```
backend/
├── app/
│   ├── routes/         ← Définition des endpoints REST (ex: /check, /autocomplete, /translate)
│   └── modules/        ← Un fichier Python par fonctionnalité IA (voir détail ci-dessous)
├── main.py             ← Point d'entrée FastAPI, déclaration de l'app et des routes
└── requirements.txt    ← Dépendances Python à installer
```

**Détail des modules IA (`app/modules/`) :**

| Fichier | Responsabilité |
|---|---|
| `spell_checker.py` | Correction orthographique via dictionnaire + distance de Levenshtein (rapidfuzz) |
| `lemmatizer.py` | Lemmatisation par analyse des préfixes et suffixes malagasy |
| `ngram_model.py` | Chargement et inférence du modèle N-gram pour l'autocomplétion |
| `ner.py` | Détection des entités nommées (villes, personnalités) depuis une liste locale |
| `sentiment.py` | Analyse de sentiment positif/négatif par Bag of Words |
| `tts.py` | Synthèse vocale du texte avec gTTS |
| `translator.py` | Traduction mot-à-mot via dictionnaire local ou API Wikipedia |
| `chatbot.py` | Co-pilote IA pour répondre aux questions de conjugaison et synonymes |

> Chaque module expose des fonctions Python pures, appelées depuis les routes. Il n'y a pas de logique métier dans `routes/`, uniquement la réception et la réponse HTTP.

---

### `frontend/`

Contient l'interface utilisateur de l'éditeur. Le frontend est totalement libre dans ses choix technologiques et dans l'organisation interne de son code. L'unique contrainte est qu'il consomme les endpoints exposés par le backend via des appels HTTP.

```
frontend/
├── src/
│   ├── components/     ← Composants visuels de l'éditeur (éditeur principal, barre d'outils, panneau latéral, chatbot, etc.)
│   ├── hooks/          ← Logique réutilisable liée aux appels API (correction, autocomplétion, etc.)
│   └── ...             ← Le frontend organise le reste comme il le souhaite
├── index.html
└── package.json
```

> Le frontend est responsable de l'expérience utilisateur : fluidité, design, intégration des suggestions inline, affichage des traductions au clic droit, badges de sentiment, etc. L'équipe frontend décide librement de ses composants et de son architecture interne.

---

### `data/`

Contient toutes les ressources statiques utilisées par les modules IA du backend. Ces fichiers sont construits en amont via les scripts du dossier `scripts/`, puis chargés en mémoire au démarrage du serveur.

```
data/
├── dictionary.json       ← Liste de mots malagasy valides (source : tenymalagasy.org + Wikipedia)
├── wikipedia_mg.txt      ← Corpus de textes bruts extraits de Wikipedia MG (pour N-grams)
├── bible_mg.txt          ← Corpus de la Bible malagasy (texte propre, formel)
├── ngram_model.pkl       ← Modèle N-gram sérialisé (généré par build_ngrams.py, ne pas éditer manuellement)
├── entities_mg.json      ← Liste des entités nommées : villes, noms propres, institutions
├── affixes.json          ← Préfixes et suffixes malagasy utilisés pour la lemmatisation
└── sentiment_words.json  ← Lexique de mots positifs et négatifs pour l'analyse de sentiment
```

> Ces fichiers sont des données de référence. Ils ne doivent pas être modifiés à la main sauf pour ajouter des entrées au dictionnaire ou au lexique de sentiment. Le fichier `.pkl` est toujours regénéré en lançant `scripts/build_ngrams.py`.

---

### `scripts/`

Contient les scripts de préparation des données. Ces scripts sont exécutés **une seule fois** pour construire les fichiers du dossier `data/`. Ils ne font pas partie de l'application en production.

```
scripts/
├── scrape_wiki.py        ← Télécharge et nettoie les articles de mg.wikipedia.org via l'API MediaWiki
├── scrape_teny.py        ← Scrape tenymalagasy.org pour extraire le dictionnaire malagasy
├── build_dict.py         ← Fusionne et déduplique les sources pour produire dictionary.json
├── build_ngrams.py       ← Entraîne le modèle N-gram sur les corpus et sérialise ngram_model.pkl
└── extract_entities.py   ← Extrait les noms de lieux et personnalités depuis Wikipedia pour entities_mg.json
```

> Pour régénérer toutes les données depuis zéro, exécuter les scripts dans cet ordre :
> `scrape_wiki.py` → `scrape_teny.py` → `build_dict.py` → `build_ngrams.py` → `extract_entities.py`

---

## Fonctionnalités IA

| Fonctionnalité | Approche | Module |
|---|---|---|
| Correcteur orthographique | Dictionnaire + Levenshtein | `spell_checker.py` |
| Vérification phonotactique | REGEX (combinaisons interdites : `nb`, `mk`, `dt`…) | `spell_checker.py` |
| Lemmatisation | Règles sur préfixes/suffixes malagasy | `lemmatizer.py` |
| Autocomplétion | Modèle N-gram (bigramme/trigramme) | `ngram_model.py` |
| Traducteur mot-à-mot | Dictionnaire local + API Wikipedia MG | `translator.py` |
| Analyse de sentiment | Bag of Words + lexique malagasy | `sentiment.py` |
| Synthèse vocale (TTS) | gTTS avec code langue `mg` | `tts.py` |
| Reconnaissance d'entités (NER) | Liste locale + Wikipedia | `ner.py` |
| Chatbot assistant | Claude API (Anthropic) | `chatbot.py` |

---

## Installation et lancement

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Préparer les données (une seule fois)

```bash
cd scripts
python scrape_wiki.py
python scrape_teny.py
python build_dict.py
python build_ngrams.py
python extract_entities.py
```

---

## Variables d'environnement

Copier `.env.example` en `.env` et renseigner les valeurs :

```
ANTHROPIC_API_KEY=sk-...        # Pour le chatbot assistant
LIBRETRANSLATE_URL=...          # Optionnel, si auto-hébergé
```

---

## Bibliographie

- Wikipedia Malagasy API : https://mg.wikipedia.org/w/api.php
- Tenymalagasy.org : https://www.tenymalagasy.org
- rapidfuzz (Levenshtein) : https://github.com/maxbachmann/RapidFuzz
- gTTS : https://gtts.readthedocs.io
- FastAPI : https://fastapi.tiangolo.com
- Quill.js : https://quilljs.com
- LibreTranslate : https://libretranslate.com
- NLTK N-grams : https://www.nltk.org

---

## Évolution prévue (avant le 14 avril 2026)

_À compléter par l'équipe : nouvelles fonctionnalités planifiées, améliorations de l'UX, optimisations des modèles NLP..._