# Editeur de Texte Augmente par l'IA pour le Malagasy

Projet TP Machine Learning — Institut Superieur Polytechnique de Madagascar (ISPM)
Master 2 — Semestre 1

# Lien du projet
frontend : 
- Railway : https://malagasy-frontend-production.up.railway.app/editor
- Render : https://malagasy-frontend.onrender.com/editor 
backend-proxy : 
- Railway : https://malagasy-proxy-production.up.railway.app/
- Render : https://malagasy-proxy.onrender.com
backend-python : 
- Railway : https://malagasy-python-production.up.railway.app/
- Render : https://malagasy-python.onrender.com

---

## Membres du groupe

| Nom                        | Role                                            |
| -------------------------- | ------------------------------------------------|
| Johaninho                  | Chef de projet / Backend Proxy / Bot / frontend |
| Leonel                     | Backend / modeles NLP                           |
| Dilan                      | Frontend                                        |
| Koloina                    | UI/UX                                           |
| Zo Bryan, Manitra, Koloina | NLP / Data                                      |
| Johaninho, Dilan, Leonel   | DevOps / Integration                            |

---

## Presentation du projet

Editeur de texte web intelligent pour le Malagasy, langue a faibles ressources numeriques. L'outil combine des approches symboliques, algorithmiques et statistiques pour proposer de la correction orthographique, de l'autocompletion, de la traduction, de l'analyse de sentiment et un chatbot assistant.

---

## Architecture

```
frontend (Next.js)
     |
     | HTTP (NEXT_PUBLIC_PROXY_URL)
     v
backend-proxy (Node.js / Express)
     |
     |-- Google APIs (Translate, TTS, NER, Sentiment, Chat via Gemini)
     |
     | HTTP (PYTHON_BACKEND_URL)
     v
backend-python (FastAPI)
     |
     v
data/ (dictionnaire, corpus, affixes)
```

- Le **frontend** ne parle jamais directement au backend Python.
- Le **proxy** centralise la securite (CORS, rate limiting, helmet, cache Redis optionnel).
- Le **backend Python** est interne uniquement (non expose publiquement).

---

## Stack technique

| Couche          | Technologie                                      |
| --------------- | ------------------------------------------------ |
| Frontend        | Next.js 14, TypeScript, React Query, CSS Modules |
| Backend Proxy   | Node.js 20, Express, Helmet, express-rate-limit  |
| Backend IA      | Python 3.11, FastAPI, RapidFuzz, uvicorn         |
| Cache           | Redis 7 (optionnel, degradation propre si absent)|
| IA externe      | Google Gemini (chat, NER, sentiment), Google TTS, Google Translate |
| Deploiement     | Render (Blueprint render.yaml), Docker           |

---

## Structure du projet

```
.
├── frontend/               # Application Next.js (port 3000)
│   ├── app/                # Pages et layout (App Router)
│   ├── components/         # Composants atoms / molecules / organisms
│   ├── features/           # Panneaux : chatbot, editeur, spellcheck, traduction
│   ├── hooks/              # Hooks React (useAutocomplete, useSpellcheck, ...)
│   ├── services/           # Clients HTTP (apiClient.ts)
│   ├── types/              # Types TypeScript partages
│   └── Dockerfile
├── backend-proxy/          # Proxy Node.js/Express (port 8000)
│   ├── src/
│   │   ├── server.js       # Point d'entree, middlewares globaux
│   │   ├── routes/         # autocomplete, translate, tts, ner, sentiment, chat
│   │   ├── middleware/     # cache Redis, validation express-validator
│   │   └── gemini.js       # Client Google Gemini avec fallback multi-modeles
│   └── Dockerfile
├── backend/                # API Python FastAPI (port 10000)
│   ├── app/
│   │   ├── main.py         # Routes FastAPI
│   │   └── modules/        # spell_checker, lemmatizer, ngram_model
│   └── dockerfile
├── data/                   # Donnees partagees (dictionnaire, corpus, affixes)
├── scripts/                # Scripts de collecte et nettoyage de donnees
├── render.yaml             # Blueprint Render (deploiement des 3 services)
├── docker-compose.yml      # Orchestration locale (frontend + proxy + python + redis)
└── .env.example            # Variables d'environnement requises
```

---

## Fonctionnalites IA

| Fonctionnalite             | Approche                                              | Implemente dans       
| -------------------------- | ----------------------------------------------------- |
| Correction orthographique  | Dictionnaire + distance de Levenshtein (rapidfuzz)    | backend Python
| Verification phonotactique | REGEX (combinaisons interdites : nb, mk, dt, sz...)   | backend Python        |
| Lemmatisation              | Regles prefixes/suffixes malagasy                     | backend Python        |
| Autocompletion             | Modele N-gram (bigramme/trigramme) sur corpus Bible   | backend Python        |
| Traduction                 | Google Translate via proxy                            | backend-proxy         |
| Synthese vocale (TTS)      | Google TTS via proxy                                  | backend-proxy         |
| Analyse de sentiment       | Google Gemini via proxy                               | backend-proxy         |
| Reconnaissance d'entites   | Google Gemini via proxy                               | backend-proxy         |
| Chatbot assistant          | Google Gemini (fallback multi-modeles) via proxy      | backend-proxy         |

---

## Lancement en local

### Pre-requis
- Docker Desktop installe et demarre

### Demarrage

```bash
cp .env.example .env
# Renseigner GOOGLE_API_KEY dans .env
docker compose up --build
```

Services disponibles :
- Frontend : http://localhost:3000
- Backend Proxy : http://localhost:8000
- Backend Python : interne uniquement (port 8001)

---

## Deploiement (Render)

Le fichier `render.yaml` configure les 3 services en Blueprint Render.

1. Pousser le depot sur GitHub
2. Sur render.com : New > Blueprint > selectionner le depot
3. Apres le premier deploiement, ajouter dans les variables du service `malagasy-proxy` :
   - `GOOGLE_API_KEY`
   - `ANTHROPIC_API_KEY` (optionnel)
4. Redeclencher le deploiement

URLs produites :
- `https://malagasy-frontend.onrender.com`
- `https://malagasy-proxy.onrender.com`
- `https://malagasy-python.onrender.com` (appele uniquement par le proxy)

---

## Variables d'environnement

Copier `.env.example` en `.env` :

| Variable             | Obligatoire | Description                              |
| -------------------- | ----------- | ---------------------------------------- |
| `GOOGLE_API_KEY`     | Oui         | Cle Google (Gemini, Translate, TTS)      |
| `ANTHROPIC_API_KEY`  | Non         | Fallback chatbot Claude (optionnel)      |
| `PYTHON_BACKEND_URL` | Automatique | Defini par docker-compose / render.yaml  |
| `REDIS_URL`          | Non         | Cache Redis (degrade proprement si absent)|

---

## Bibliographie

### Sources de données

- Kaggle — jeux de données publics : https://www.kaggle.com
- GitHub — corpus et projets open-source : https://www.github.com
- Wikipedia Malagasy — articles encyclopédiques en malgache : https://mg.wikipedia.org
- JW.org — textes parallèles et corpus bilingue malagasy : https://www.jw.org
- Tenymalagasy.org — dictionnaire et ressources lexicales malagasy : https://www.tenymalagasy.org
- Wiktionnaire Malagasy — entrées lexicales et définitions : https://mg.wiktionary.org

### Bibliothèques et outils

- rapidfuzz (Levenshtein) : https://github.com/maxbachmann/RapidFuzz
- gTTS : https://gtts.readthedocs.io
- FastAPI : https://fastapi.tiangolo.com
- NLTK N-grams : https://www.nltk.org
- Google Generative Language API : https://ai.google.dev
- Render Blueprint spec : https://render.com/docs/blueprint-spec

---

## Évolution prévue (avant le 14 avril 2026)

_À compléter par l'équipe : nouvelles fonctionnalités planifiées, améliorations de l'UX, optimisations des modèles NLP..._
