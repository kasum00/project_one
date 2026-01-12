const path = require("path");
const axios = require("axios");
const pool = require("../config/database");

const ML_BASE_URL = "http://localhost:8000";

exports.findSimilar = async (userId, wardrobeItemId) => {
  // 1. Lấy item gốc
  const [[item]] = await pool.execute(
    `
    SELECT id, embedding_path
    FROM wardrobe_items
    WHERE id = ? AND user_id = ? AND is_deleted = FALSE
    `,
    [wardrobeItemId, userId]
  );

  if (!item) {
    throw new Error("Wardrobe item not found");
  }

  // 2. Gọi ML service
  const mlRes = await axios.post(`${ML_BASE_URL}/similar`, {
    embedding_path: item.embedding_path
  });

  /**
   * ML trả về dạng:
   * [
   *   { id: 45, score: 0.87 },
   *   { id: 31, score: 0.82 }
   * ]
   */
  const similarIds = mlRes.data;

  if (!Array.isArray(similarIds) || similarIds.length === 0) {
    return [];
  }

  // 3. Lấy thông tin ảnh từ DB
  const ids = similarIds.map(x => x.id);
  const placeholders = ids.map(() => "?").join(",");

  const [rows] = await pool.execute(
    `
    SELECT id, image_path
    FROM wardrobe_items
    WHERE id IN (${placeholders})
      AND is_deleted = FALSE
    `,
    ids
  );

  // 4.Gộp score + image
  return rows.map(row => {
    const match = similarIds.find(x => x.id === row.id);
    return {
      id: row.id,
      image_path: row.image_path,
      score: match?.score || 0
    };
  });
};
