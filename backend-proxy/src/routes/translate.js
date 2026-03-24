"use strict";

const router = require("express").Router();
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");
const { postWithFallback, LOW_QUOTA_SAVING_MODELS } = require("../gemini");

// Noms BCP-47 → lisibles pour le prompt
const LANG_NAMES = { mg: "Malagasy", fr: "French", en: "English", es: "Spanish", de: "German", zh: "Chinese" };

// POST /api/translate
// Body : { text: string, from?: string, to?: string }
// from/to : codes BCP-47 (ex. "mg", "fr", "en")
// Retourne : { text, from, to, translation }
router.post(
  "/",
  body("text").isString().trim().notEmpty().isLength({ max: 500 }),
  body("from").optional().isString().trim().isLength({ max: 10 }),
  body("to").optional().isString().trim().isLength({ max: 10 }),
  handleValidation,
  cache((req) => `translate:${req.body.text}:${req.body.from || "mg"}:${req.body.to || "fr"}`),
  async (req, res) => {
    const { text, from = "mg", to = "fr" } = req.body;
    const apiKey = process.env.GOOGLE_API_KEY;

    if (!apiKey) {
      return res.status(503).json({ error: "GOOGLE_API_KEY non configurée" });
    }

    const fromName = LANG_NAMES[from] || from;
    const toName   = LANG_NAMES[to]   || to;
    const prompt = `Translate the following text from ${fromName} (${from}) to ${toName} (${to}).\nReturn ONLY valid JSON in this exact format: {"translation": "<translated text>"}\n\nText:\n${text}`;

    try {
      const { data, modelUsed } = await postWithFallback({
        apiKey,
        models: LOW_QUOTA_SAVING_MODELS,
        body: {
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.1, maxOutputTokens: 1024, responseMimeType: "application/json" },
        },
      });

      const raw = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "{}";

      // Fallback : extraction du bloc JSON si Gemini répond en texte libre
      let parsed;
      try {
        parsed = JSON.parse(raw);
      } catch (_) {
        const match = raw.match(/\{[\s\S]*?\}/);
        if (!match) throw new Error("No JSON block found in Gemini response");
        parsed = JSON.parse(match[0]);
      }

      res.json({ text, from, to, translation: parsed.translation ?? "", modelUsed });
    } catch (err) {
      console.error("[translate]", err.response?.data || err.message);
      res.status(502).json({ error: "Service de traduction indisponible" });
    }
  }
);

module.exports = router;
