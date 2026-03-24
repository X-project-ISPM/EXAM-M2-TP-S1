"use strict";

const router = require("express").Router();
const axios = require("axios");
const { body } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");

const TTS_MODEL = "gemini-2.5-flash-preview-tts";
const TTS_URL = `https://generativelanguage.googleapis.com/v1beta/models/${TTS_MODEL}:generateContent`;

/**
 * Gemini TTS renvoie du PCM brut (audio/L16) sans en-tête RIFF.
 * Cette fonction encapsule les bytes PCM dans un conteneur WAV valide
 * que tous les navigateurs peuvent lire nativement.
 */
function pcmToWav(pcmBuffer, sampleRate = 24000, numChannels = 1, bitsPerSample = 16) {
  const dataLength = pcmBuffer.length;
  const buffer = Buffer.alloc(44 + dataLength);

  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);                                          // PCM chunk size
  buffer.writeUInt16LE(1, 20);                                           // AudioFormat = PCM
  buffer.writeUInt16LE(numChannels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * numChannels * bitsPerSample / 8, 28); // ByteRate
  buffer.writeUInt16LE(numChannels * bitsPerSample / 8, 32);             // BlockAlign
  buffer.writeUInt16LE(bitsPerSample, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataLength, 40);
  pcmBuffer.copy(buffer, 44);

  return buffer;
}

// Voix disponibles : Aoede, Charon, Fenrir, Kore, Orbit, Puck, Schedar, Sulafat
// POST /api/tts
// Body : { text: string, voice?: string }
// Retourne : { audio: "<base64 WAV>", format: "wav", mimeType: string, encoding: "base64" }
// Le frontend peut lire l'audio via : new Audio("data:audio/wav;base64," + audio).play()
router.post(
  "/",
  body("text").isString().trim().notEmpty().isLength({ max: 1000 }),
  body("voice").optional().isString().trim().isLength({ max: 50 }),
  handleValidation,
  cache((req) => `tts:${req.body.text}:${req.body.voice || "Aoede"}`, 86400), // cache 24h
  async (req, res) => {
    const { text, voice = "Aoede" } = req.body;
    const apiKey = process.env.GOOGLE_API_KEY;

    if (!apiKey) {
      return res.status(503).json({ error: "GOOGLE_API_KEY non configurée" });
    }

    try {
      const { data } = await axios.post(
        TTS_URL,
        {
          contents: [{ parts: [{ text }] }],
          generationConfig: {
            responseModalities: ["AUDIO"],
            speechConfig: {
              voiceConfig: {
                prebuiltVoiceConfig: { voiceName: voice },
              },
            },
          },
        },
        { params: { key: apiKey } }
      );

      const inlineData = data.candidates?.[0]?.content?.parts?.[0]?.inlineData;
      if (!inlineData?.data) {
        // Certains modèles retournent le texte dans parts au lieu d'inlineData
        const errDetail = data.candidates?.[0]?.finishReason || "inlineData absent";
        console.error("[tts] Pas d'audio reçu, finishReason:", errDetail, JSON.stringify(data).slice(0, 300));
        return res.status(502).json({ error: "Service TTS indisponible" });
      }

      // Extraire le sample rate depuis le mimeType (ex: "audio/L16;codec=pcm;rate=24000")
      const rateMatch = (inlineData.mimeType || "").match(/rate=(\d+)/);
      const sampleRate = rateMatch ? parseInt(rateMatch[1], 10) : 24000;

      // Gemini retourne du PCM brut (L16) — on l'encapsule dans un WAV valide
      const pcmBuffer = Buffer.from(inlineData.data, "base64");
      const wavBuffer = pcmToWav(pcmBuffer, sampleRate);

      res.json({
        audio: wavBuffer.toString("base64"),
        format: "wav",
        mimeType: "audio/wav",
        encoding: "base64",
      });
    } catch (err) {
      console.error("[tts]", err.response?.data || err.message);
      res.status(502).json({ error: "Service TTS indisponible" });
    }
  }
);

module.exports = router;
