"use strict";

require("dotenv").config();

const express = require("express");
const helmet = require("helmet");
const cors = require("cors");
const morgan = require("morgan");
const rateLimit = require("express-rate-limit");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 8000;

// ─── Playground statique ───────────────────────────────────────
app.use(express.static(path.join(__dirname, "..", "public")));

// ─── Middlewares de sécurité ───────────────────────────────────
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc:  ["'self'", "'unsafe-inline'"], // requis pour le playground inline JS
        styleSrc:   ["'self'", "'unsafe-inline'"],
        mediaSrc:   ["'self'", "data:"],            // lecture audio base64 TTS
        connectSrc: ["'self'"],
      },
    },
  })
);
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:3000" }));
app.use(morgan("dev"));
app.use(express.json({ limit: "50kb" })); // limite la taille du body

// ─── Rate limiting global (60 req/min par IP) ────────────────
app.use(
  rateLimit({
    windowMs: 60 * 1000,
    max: 60,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Trop de requêtes, réessayez dans une minute." },
  })
);

// ─── Health check ─────────────────────────────────────────────
app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "backend-proxy" });
});

// ─── Routes gérées directement par le proxy (Google APIs) ─────
app.use("/api/translate",  require("./routes/translate"));
app.use("/api/tts",        require("./routes/tts"));
app.use("/api/ner",        require("./routes/ner"));
app.use("/api/sentiment",  require("./routes/sentiment"));
app.use("/api/chat",       require("./routes/chat"));

// ─── Routes déléguées au backend Python distant ─────────────────
app.use("/api/autocomplete", require("./routes/autocomplete"));

// ─── Routes Python supplémentaires (à activer quand disponibles) ─
// app.use("/api/spellcheck",   require("./routes/spellcheck"));
// app.use("/api/lemmatize",    require("./routes/lemmatize"));

// ─── Démarrage ────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`[proxy] Serveur démarré sur le port ${PORT}`);
});
