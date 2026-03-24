FROM node:20-alpine

WORKDIR /app

# Copier les manifestes en premier pour profiter du cache Docker
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

# Copier le code source
COPY src/ ./src/

EXPOSE 8000

CMD ["node", "src/server.js"]
