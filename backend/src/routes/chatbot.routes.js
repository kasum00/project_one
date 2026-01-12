const express = require("express");
const router = express.Router();
const auth = require("../middleware/auth.middleware");
const ctrl = require("../controllers/chatbot.controller");

router.post("/similar", auth, ctrl.findSimilarItem);
router.post("/outfit", auth, ctrl.findMatchingOutfit);

module.exports = router;
