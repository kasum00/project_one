const express = require("express");
const router = express.Router();

const auth = require("../middleware/auth.middleware");
const upload = require("../middleware/upload.middleware");
const controller = require("../controllers/wardrobe.controller");

router.post(
  "/upload",
  auth,
  upload.array("image",1000000000),
  controller.uploadItem
);

router.get("/", auth, controller.getWardrobe);

router.put("/:id/label", auth, controller.updateLabel);

module.exports = router;
