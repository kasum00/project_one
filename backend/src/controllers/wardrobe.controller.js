const wardrobeService = require("../services/wardrobe.service");

/**
 * POST /api/wardrobe/upload
 */
exports.uploadItem = async (req, res) => {
  try {
    const userId = req.user.id;
    const results = [];

    for (const file of req.files) {
      
      const imagePath = `uploads/wardrobe/${file.filename}`;

      const data = await wardrobeService.processUpload(
        userId,
        imagePath
      );

      results.push(data);
    }

    res.status(201).json({
      success: true,
      data: results
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Upload failed" });
  }
};

/**
 * GET /api/wardrobe?category=bottoms
 */
exports.getWardrobe = async (req, res) => {
  try {
    const category = req.query.category || null;

    const items = await wardrobeService.getItems(
      req.user.id,
      category
    );

    res.json(items);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Get wardrobe failed" });
  }
};

/**
 * PUT /api/wardrobe/:id/label
 */
exports.updateLabel = async (req, res) => {
  try {
    const { id } = req.params;
    const { user_label } = req.body;

    await wardrobeService.updateLabel(
      id,
      req.user.id,
      user_label
    );

    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ success: false });
  }
};
