"use strict";

const Redis = require("ioredis");
const crypto = require("crypto");

let redis = null;

try {
  redis = new Redis(process.env.REDIS_URL || "redis://localhost:6379", {
    lazyConnect: true,
    enableOfflineQueue: false,
  });
  redis.on("error", (e) => {
    console.warn("[cache] Redis indisponible, mode sans cache :", e.message);
    redis = null;
  });
} catch {
  redis = null;
}

const DEFAULT_TTL = 3600; // 1 heure

/**
 * Middleware de cache Redis.
 * @param {(req: Request) => string} keyFn  Fonction qui calcule la clé logique depuis la requête.
 * @param {number} ttl  Durée de vie du cache en secondes.
 */
const cache = (keyFn, ttl = DEFAULT_TTL) => async (req, res, next) => {
  if (!redis) return next();

  // Hachage SHA-256 pour éviter les clés trop longues ou les injections Redis
  const raw = `proxy:${keyFn(req)}`;
  const key = crypto.createHash("sha256").update(raw).digest("hex");

  try {
    const cached = await redis.get(key);
    if (cached) {
      res.setHeader("X-Cache", "HIT");
      return res.json(JSON.parse(cached));
    }
  } catch {
    /* Redis down → on continue sans cache */
  }

  // Intercepter res.json pour stocker la réponse dans Redis
  // Ne mettre en cache que les réponses 2xx — jamais les erreurs
  const originalJson = res.json.bind(res);
  res.json = (data) => {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      redis.set(key, JSON.stringify(data), "EX", ttl).catch(() => {});
      res.setHeader("X-Cache", "MISS");
    }
    return originalJson(data);
  };

  next();
};

module.exports = { cache };
