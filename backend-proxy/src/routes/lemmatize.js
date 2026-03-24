"use strict";

const router = require("express").Router();
const axios = require("axios");
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");

// POST /api/lemmatize
// Body : { word: string }
// Appelle le backend Python GET /lemmatize/{word}
// Retourne : { original, root, is_root }
router.post(
  "/",
  body("word").isString().trim().notEmpty().isLength({ max: 100 }),
  handleValidation,
  cache((req) => `lemmatize:${req.body.word}`, 3600),
  async (req, res) => {
    const { word } = req.body;
    const baseUrl = process.env.PYTHON_BACKEND_URL || "http://backend-python:8001";

    try {
      const { data } = await axios.get(
        `${baseUrl}/lemmatize/${encodeURIComponent(word)}`,
        { timeout: 5000 }
      );

      res.json(data);
    } catch (err) {
      if (err.code === "ECONNREFUSED" || err.code === "ECONNABORTED" || err.code === "ETIMEDOUT") {
        console.error("[lemmatize] Backend Python injoignable :", err.message);
        return res.status(503).json({ error: "Service lemmatize indisponible" });
      }
      console.error("[lemmatize]", err.response?.data || err.message);
      res.status(502).json({ error: "Erreur du service lemmatize" });
    }
  }
);

module.exports = router;
