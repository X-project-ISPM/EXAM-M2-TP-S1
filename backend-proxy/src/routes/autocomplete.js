"use strict";

const router = require("express").Router();
const axios = require("axios");
const { query } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");

// GET /api/autocomplete?text=...
// Proxie vers le backend Python distant (192.168.1.120)
// Retourne : { suggestions: string[], type?: "prediction"|"correction" }
//         ou { suggestions: string[], error: string, type: "correction" }
//         ou { suggestions: [] }
router.get(
  "/",
  query("text").isString().trim().notEmpty().isLength({ max: 500 }),
  handleValidation,
  cache((req) => `autocomplete:${req.query.text}`, 300), // cache 5 min
  async (req, res) => {
    const { text } = req.query;
    const baseUrl = process.env.PYTHON_BACKEND_URL || "http://192.168.1.120";

    try {
      const { data } = await axios.get(`${baseUrl}/autocomplete`, {
        params: { text },
        timeout: 8000,
      });

      res.json(data);
    } catch (err) {
      if (err.code === "ECONNREFUSED" || err.code === "ECONNABORTED" || err.code === "ETIMEDOUT") {
        console.error("[autocomplete] Backend Python injoignable :", err.message);
        return res.status(503).json({ error: "Service autocomplete indisponible (backend Python hors ligne)" });
      }
      console.error("[autocomplete]", err.response?.data || err.message);
      res.status(502).json({ error: "Erreur du service autocomplete" });
    }
  }
);

module.exports = router;
