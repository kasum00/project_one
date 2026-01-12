const express = require("express");
const router = express.Router();
const axios = require("axios");
const WardrobeItem = require("../models/WardrobeItem");

// ML service URL
const ML_URL = "http://127.0.0.1:8000";

// ============================
// FIND SIMILAR ITEM
// ============================
router.post("/similar", async (req, res) => {
  try {
    const { itemId } = req.body;

    if (!itemId) {
      return res.status(400).json({ message: "itemId is required" });
    }

    // 1️⃣ Load wardrobe item
    const item = await WardrobeItem.findById(itemId);
    if (!item) {
      return res.status(404).json({ message: "Item not found" });
    }

    const imagePath = item.image_path;

    // 2️⃣ Embed image
    const embedRes = await axios.post(`${ML_URL}/embed`, {
      image_path: imagePath
    });

    const embeddingPath = embedRes.data.embedding_path;

    // 3️⃣ Recommend similar
    const recRes = await axios.post(`${ML_URL}/recommend`, {
      embedding_path: embeddingPath,
      top_k: 5
    });

    // 4️⃣ Map item_key → DB items
    const results = await Promise.all(
      recRes.data.map(async r => {
        return WardrobeItem.findOne({ item_key: r.item_key });
      })
    );

    res.json({
      items: results.filter(Boolean)
    });

  } catch (err) {
    console.error("SIMILAR ERROR:", err.message);
    res.status(500).json({ message: "Internal server error" });
  }
});

// ============================
// FIND OUTFIT
// ============================
router.post("/outfit", async (req, res) => {
  try {
    const { itemId } = req.body;

    if (!itemId) {
      return res.status(400).json({ message: "itemId is required" });
    }

    const item = await WardrobeItem.findById(itemId);
    if (!item) {
      return res.status(404).json({ message: "Item not found" });
    }

    // ⚠️ Outfit dùng ML outfit logic của bạn
    // Ở đây giả sử bạn expose endpoint /outfit trong ML
    const mlRes = await axios.post(`${ML_URL}/outfit`, {
      image_path: item.image_path
    });

    const outfitItems = await Promise.all(
      mlRes.data.map(o =>
        WardrobeItem.findOne({ item_key: o.item_key })
      )
    );

    res.json({
      outfit: outfitItems.filter(Boolean)
    });

  } catch (err) {
    console.error("OUTFIT ERROR:", err.message);
    res.status(500).json({ message: "Internal server error" });
  }
});

module.exports = router;
