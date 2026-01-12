const express = require("express");
const router = express.Router();
const auth = require("../middleware/auth.middleware");
const recommendController = require("../controllers/recommend.controller");

router.post("/similar", auth, recommendController.findSimilar);

module.exports = router;
