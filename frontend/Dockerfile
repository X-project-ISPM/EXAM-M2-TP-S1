# ─────────────────────────────────────────────────────────────────
# Stage 1 — Installer les dépendances
# ─────────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# ─────────────────────────────────────────────────────────────────
# Stage 2 — Builder l'application Next.js
# ─────────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# La variable est définie dans docker-compose via build.args
ARG NEXT_PUBLIC_PROXY_URL=http://localhost:8000
ENV NEXT_PUBLIC_PROXY_URL=$NEXT_PUBLIC_PROXY_URL

RUN npm run build

# ─────────────────────────────────────────────────────────────────
# Stage 3 — Image de production (runner minimal)
# ─────────────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Créer un utilisateur non-root pour la sécurité
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
