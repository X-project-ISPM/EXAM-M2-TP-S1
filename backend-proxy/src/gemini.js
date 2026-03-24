"use strict";

const axios = require("axios");

const DEFAULT_MODELS = [
  "gemini-3.1-flash-lite-preview",
  "gemini-2.5-flash-lite",
  "gemini-2.5-flash",
];

const LOW_QUOTA_SAVING_MODELS = [
  "gemma-3-4b-it",
  "gemma-3-12b-it",
  "gemma-3-27b-it",
  "gemini-3.1-flash-lite-preview",
  "gemini-2.5-flash-lite",
  "gemini-2.5-flash",
];

async function postWithFallback({ apiKey, body, models = DEFAULT_MODELS }) {
  let lastError;

  for (const model of models) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

    try {
      const response = await axios.post(url, body, { params: { key: apiKey } });
      return {
        data: response.data,
        modelUsed: model,
      };
    } catch (err) {
      lastError = err;
      const status = err.response?.data?.error?.status;
      const code = err.response?.data?.error?.code;
      const message = err.response?.data?.error?.message || "";
      const gemmaJsonModeUnsupported = code === 400 && /JSON mode is not enabled/i.test(message);

      if (
        status === "UNAVAILABLE" ||
        status === "RESOURCE_EXHAUSTED" ||
        code === 429 ||
        code === 503 ||
        code === 404 ||
        gemmaJsonModeUnsupported
      ) {
        continue;
      }

      throw err;
    }
  }

  throw lastError || new Error("Aucun modèle Gemini disponible");
}

module.exports = {
  DEFAULT_MODELS,
  LOW_QUOTA_SAVING_MODELS,
  postWithFallback,
};