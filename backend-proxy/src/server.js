"use strict";

require("dotenv").config();

const express = require("express");
const helmet = require("helmet");
const cors = require("cors");
const morgan = require("morgan");

const app = express();
const PORT = process.env.PORT || 8000;

// ─── Middlewares de sécurité ───────────────────────────────────
app.use(helmet());
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:3000" }));
app.use(morgan("dev"));
app.use(express.json());

// ─── Health check ─────────────────────────────────────────────
app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "backend-proxy" });
});

// ─── Routes API (à compléter) ─────────────────────────────────
// app.use("/api/spellcheck", require("./routes/spellcheck"));
// app.use("/api/translate",  require("./routes/translate"));
// app.use("/api/autocomplete", require("./routes/autocomplete"));
// app.use("/api/tts",        require("./routes/tts"));
// app.use("/api/chat",       require("./routes/chat"));

// ─── Démarrage ────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`[proxy] Serveur démarré sur le port ${PORT}`);
});
