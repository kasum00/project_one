const chatbotService = require("../services/chatbot.service");

// 1 FIND SIMILAR ITEM
exports.findSimilarItem = async (req, res) => {
  try {
    const { itemId } = req.body;

    const items = await chatbotService.findSimilarItem(
      req.user.id,
      itemId
    );

    res.json({
      mode: "similar",
      items
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: err.message });
  }
};

// 2 FIND MATCHING OUTFIT
exports.findMatchingOutfit = async (req, res) => {
  try {
    const { itemId } = req.body;

    const outfit = await chatbotService.findMatchingOutfit(
      req.user.id,
      itemId
    );

    res.json({
      mode: "outfit",
      outfit
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: err.message });
  }
};
