"use strict";

const router = require("express").Router();
const axios = require("axios");
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");

const GEMINI_MODEL = "gemini-2.5-flash";
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

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

    // Construction du fil de conversation pour l'API Gemini
    const contents = [
      ...history.map((h) => ({
        role: h.role,
        parts: [{ text: h.text }],
      })),
      { role: "user", parts: [{ text: message }] },
    ];

    try {
      const { data } = await axios.post(
        GEMINI_URL,
        {
          system_instruction: { parts: [{ text: SYSTEM_PROMPT }] },
          contents,
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 512,
          },
        },
        { params: { key: apiKey } }
      );

      const reply = data.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
      res.json({ reply });
    } catch (err) {
      console.error("[chat]", err.response?.data || err.message);
      res.status(502).json({ error: "Service chatbot indisponible" });
    }
  }
);

module.exports = router;
