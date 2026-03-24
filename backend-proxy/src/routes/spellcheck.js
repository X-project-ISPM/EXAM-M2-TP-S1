"use strict";

const router = require("express").Router();
const axios = require("axios");
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");

// POST /api/spellcheck
// Body : { text: string }
// Tokenise le texte, vérifie chaque mot via le backend Python,
// et retourne un tableau d'erreurs avec positions.
router.post(
  "/",
  body("text").isString().trim().notEmpty().isLength({ max: 5000 }),
  handleValidation,
  cache((req) => `spellcheck:${req.body.text}`, 300),
  async (req, res) => {
    const { text } = req.body;
    const baseUrl = process.env.PYTHON_BACKEND_URL || "http://backend-python:8001";

    // Tokeniser le texte en mots avec leurs positions
    const wordRegex = /[a-zA-ZÀ-ÿ]+/g;
    const tokens = [];
    let match;
    while ((match = wordRegex.exec(text)) !== null) {
      tokens.push({ word: match[0], offset: match.index, length: match[0].length });
    }

    if (tokens.length === 0) {
      return res.json({ errors: [] });
    }

    try {
      // Vérifier chaque mot en parallèle
      const results = await Promise.all(
        tokens.map(async (token) => {
          try {
            const { data } = await axios.get(`${baseUrl}/check`, {
              params: { word: token.word },
              timeout: 5000,
            });
            return { ...token, ...data };
          } catch {
            return { ...token, is_correct: true, suggestions: [] };
          }
        })
      );

      // Filtrer les mots incorrects
      const errors = results
        .filter((r) => !r.is_correct)
        .map((r) => ({
          word: r.word,
          offset: r.offset,
          length: r.length,
          suggestions: r.suggestions || [],
        }));

      res.json({ errors });
    } catch (err) {
      if (err.code === "ECONNREFUSED" || err.code === "ECONNABORTED" || err.code === "ETIMEDOUT") {
        console.error("[spellcheck] Backend Python injoignable :", err.message);
        return res.status(503).json({ error: "Service spellcheck indisponible" });
      }
      console.error("[spellcheck]", err.message);
      res.status(502).json({ error: "Erreur du service spellcheck" });
    }
  }
);

module.exports = router;
