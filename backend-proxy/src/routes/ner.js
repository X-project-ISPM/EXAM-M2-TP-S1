"use strict";

const router = require("express").Router();
const axios = require("axios");
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");

const GEMINI_MODEL = "gemini-3.1-flash-lite";
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

// POST /api/ner
// Body : { text: string }
// Retourne : { text, entities: [{ name, type, salience }] }
// Types : PERSON, LOCATION, ORGANIZATION, EVENT, WORK_OF_ART, CONSUMER_GOOD, OTHER
router.post(
  "/",
  body("text").isString().trim().notEmpty().isLength({ max: 2000 }),
  handleValidation,
  cache((req) => `ner:${req.body.text}`),
  async (req, res) => {
    const { text } = req.body;
    const apiKey = process.env.GOOGLE_API_KEY;

    if (!apiKey) {
      return res.status(503).json({ error: "GOOGLE_API_KEY non configurée" });
    }

    const prompt = `Extract all named entities from the text below.
For each entity provide:
- name: the exact string as it appears
- type: one of PERSON, LOCATION, ORGANIZATION, EVENT, WORK_OF_ART, CONSUMER_GOOD, OTHER
- salience: importance score 0.0 (least) to 1.0 (most)

Return ONLY valid JSON: {"entities": [{"name": "...", "type": "...", "salience": 0.0}]}

Text:
${text}`;

    try {
      const { data } = await axios.post(
        GEMINI_URL,
        {
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.0, maxOutputTokens: 1024, responseMimeType: "application/json" },
        },
        { params: { key: apiKey } }
      );

      const raw = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "{\"entities\":[]}";

      // Fallback : extraction du bloc JSON si Gemini répond en texte libre
      let parsed;
      try {
        parsed = JSON.parse(raw);
      } catch (_) {
        const match = raw.match(/\{[\s\S]*\}/);
        if (!match) throw new Error("No JSON block found in Gemini response");
        parsed = JSON.parse(match[0]);
      }

      const entities = (parsed.entities || []).map((e) => ({
        name: e.name,
        type: e.type,
        salience: typeof e.salience === "number" ? e.salience : 0,
      }));

      res.json({ text, entities });
    } catch (err) {
      console.error("[ner]", err.response?.data || err.message);
      res.status(502).json({ error: "Service NER indisponible" });
    }
  }
);

module.exports = router;
