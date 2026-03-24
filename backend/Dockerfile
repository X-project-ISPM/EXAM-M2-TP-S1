FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les dépendances depuis le dossier 'backend' (contexte de build)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu du dossier 'backend' dans /app du conteneur
COPY . .

# Définir le port (Render utilise 10000 par défaut)
ENV PORT=10000

# Commande de lancement : on utilise "app.main:app" 
# car main.py est dans le dossier app/
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]