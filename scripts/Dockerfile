FROM python:3.11-slim

WORKDIR /app

# Dépendances scraping + NLP
RUN pip install --no-cache-dir requests beautifulsoup4 urllib3

# Copier les scripts
COPY scripts/ /app/scripts/

# Le dossier data/ sera monté en volume (lecture/écriture)
# Le dossier backend/data/ sera monté en volume (écriture pour copie)

CMD ["python", "scripts/run_pipeline.py"]
