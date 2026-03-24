"use strict";

const { validationResult } = require("express-validator");

/**
 * Middleware terminal : renvoie 400 si express-validator a détecté des erreurs.
 */
const handleValidation = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
};

module.exports = { handleValidation };
