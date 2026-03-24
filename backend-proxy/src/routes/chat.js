"use strict";

const router = require("express").Router();
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { postWithFallback } = require("../gemini");

const MAX_HISTORY_ITEMS = 4;
const MAX_HISTORY_TEXT_LENGTH = 400;
const MAX_MESSAGE_LENGTH = 800;

const SYSTEM_PROMPT = `Tu es un assistant linguistique spécialisé en langue malgache.
Tu aides les rédacteurs avec la conjugaison, les synonymes, la grammaire malgache, et réponds aux questions sur la langue.
Réponds de manière concise, claire et précise. Si la question n'est pas liée à la langue malgache, redirige poliment l'utilisateur.`;

// POST /api/chat
// Body : { message: string, history?: [{ role: "user"|"model", text: string }] }
// Retourne : { reply: string }
// Pas de cache (conversationnel)
router.post(
  "/",
  body("message").isString().trim().notEmpty().isLength({ max: 2000 }),
  body("history").optional().isArray({ max: 20 }),
  body("history.*.role").optional().isIn(["user", "model"]),
  body("history.*.text").optional().isString().trim().isLength({ max: 2000 }),
  handleValidation,
  async (req, res) => {
    const { message, history = [] } = req.body;
    const apiKey = process.env.GOOGLE_API_KEY;

    if (!apiKey) {
      return res.status(503).json({ error: "GOOGLE_API_KEY non configurée" });
    }

    const trimmedMessage = message.slice(0, MAX_MESSAGE_LENGTH);
    const recentHistory = history.slice(-MAX_HISTORY_ITEMS).map((entry) => ({
      role: entry.role,
      text: entry.text.slice(0, MAX_HISTORY_TEXT_LENGTH),
    }));

    // Construction du fil de conversation pour l'API Gemini
    const contents = [
      ...recentHistory.map((h) => ({
        role: h.role,
        parts: [{ text: h.text }],
      })),
      { role: "user", parts: [{ text: trimmedMessage }] },
    ];

    try {
      const { data, modelUsed } = await postWithFallback({
        apiKey,
        body: {
          system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
          contents,
          generationConfig: {
            temperature: 0.5,
            maxOutputTokens: 256,
          },
        },
      });

      const reply = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
      res.json({ reply, modelUsed });
    } catch (err) {
      console.error("[chat]", err.response?.data || err.message);
      res.status(502).json({ error: "Service chatbot indisponible" });
    }
  }
);

module.exports = router;
