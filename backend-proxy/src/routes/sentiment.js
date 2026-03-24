"use strict";

const router = require("express").Router();
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");
const { postWithFallback, LOW_QUOTA_SAVING_MODELS } = require("../gemini");

// POST /api/sentiment
// Body : { text: string }
// Retourne : { text, score, magnitude, label }
// score : [-1.0 très négatif … +1.0 très positif]
// magnitude : intensité globale (0 = neutre)
// label : "positif" | "négatif" | "neutre"
router.post(
  "/",
  body("text").isString().trim().notEmpty().isLength({ max: 2000 }),
  handleValidation,
  cache((req) => `sentiment:${req.body.text}`),
  async (req, res) => {
    const { text } = req.body;
    const apiKey = process.env.GOOGLE_API_KEY;

    if (!apiKey) {
      return res.status(503).json({ error: "GOOGLE_API_KEY non configurée" });
    }

    const prompt = `Analyze the sentiment of the text below.
Return ONLY valid JSON in this exact format:
{"score": <number -1.0 to 1.0>, "magnitude": <number 0.0+>, "label": "<positif|négatif|neutre>"}

Rules:
- score: -1.0 = very negative, 0.0 = neutral, +1.0 = very positive
- magnitude: overall emotional intensity regardless of direction (0 = no emotion)
- label: "positif" if score > 0.2, "négatif" if score < -0.2, "neutre" otherwise

Text:
${text}`;

    try {
      const { data, modelUsed } = await postWithFallback({
        apiKey,
        models: LOW_QUOTA_SAVING_MODELS,
        body: {
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.0, maxOutputTokens: 256, responseMimeType: "application/json" },
        },
      });

      const raw = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "{}";

      // Gemini ignore parfois responseMimeType et répond en texte libre
      // → on extrait le bloc JSON par regex en fallback
      let parsed;
      try {
        parsed = JSON.parse(raw);
      } catch (_) {
        const match = raw.match(/\{[\s\S]*?\}/);
        if (!match) throw new Error("No JSON block found in Gemini response");
        parsed = JSON.parse(match[0]);
      }

      const score     = typeof parsed.score     === "number" ? parsed.score     : 0;
      const magnitude = typeof parsed.magnitude === "number" ? parsed.magnitude : 0;
      const label     = parsed.label ?? (score > 0.2 ? "positif" : score < -0.2 ? "négatif" : "neutre");

      res.json({ text, score, magnitude, label, modelUsed });
    } catch (err) {
      console.error("[sentiment]", err.response?.data || err.message);
      res.status(502).json({ error: "Service sentiment indisponible" });
    }
  }
);

module.exports = router;
