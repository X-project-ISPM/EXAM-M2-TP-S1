"use strict";

const router = require("express").Router();
const axios = require("axios");
const { query } = require("express-validator");
const { handleValidation } = require("../middleware/validate");
const { cache } = require("../middleware/cache");

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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
      let response;

      for (let attempt = 1; attempt <= 3; attempt += 1) {
        try {
          response = await axios.get(`${baseUrl}/autocomplete`, {
            params: { text },
            timeout: 50000, // 50s — cold start Render free tier
          });
          break;
        } catch (err) {
          const transientDns = err.code === "EAI_AGAIN" || err.code === "ENOTFOUND";
          const transientConn =
            err.code === "ECONNREFUSED" ||
            err.code === "ECONNABORTED" ||
            err.code === "ETIMEDOUT" ||
            err.code === "ERR_CANCELED"; // axios v1 timeout

          if ((transientDns || transientConn) && attempt < 3) {
            await sleep(500 * attempt);
            continue;
          }

          throw err;
        }
      }

      res.json({ ...response.data, modelUsed: "backend-python" });
    } catch (err) {
      const isNetworkError =
        err.code === "EAI_AGAIN" ||
        err.code === "ENOTFOUND" ||
        err.code === "ECONNREFUSED" ||
        err.code === "ECONNABORTED" ||
        err.code === "ETIMEDOUT" ||
        err.code === "ERR_CANCELED";

      console.error("[autocomplete] code=%s status=%s url=%s msg=%s",
        err.code,
        err.response?.status,
        `${baseUrl}/autocomplete`,
        err.response?.data ? JSON.stringify(err.response.data) : err.message
      );

      if (isNetworkError) {
        return res.status(503).json({ error: "Service autocomplete indisponible (backend Python hors ligne)" });
      }
      res.status(502).json({ error: "Erreur du service autocomplete" });
    }
  }
);

module.exports = router;
