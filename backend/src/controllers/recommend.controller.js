const recommendService = require("../services/recommend.service");

exports.findSimilar = async (req, res) => {
  try {
    const { wardrobe_item_id } = req.body;
    const userId = req.user.id;

    if (!wardrobe_item_id) {
      return res.status(400).json({
        success: false,
        message: "wardrobe_item_id is required"
      });
    }

    const items = await recommendService.findSimilar(
      userId,
      wardrobe_item_id
    );

    res.json({
      success: true,
      data: items
    });
  } catch (err) {
    console.error("FIND SIMILAR ERROR:", err);
    res.status(500).json({
      success: false,
      message: "Failed to find similar items"
    });
  }
};
