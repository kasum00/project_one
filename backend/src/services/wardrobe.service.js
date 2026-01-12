const path = require("path");
const axios = require("axios");
const pool = require("../config/database");

const ML_BASE_URL = "http://localhost:8000";


const UPLOAD_ROOT = path.join(process.cwd(), "src", "uploads");

exports.processUpload = async (userId, relativePath) => {
  const absImagePath = path.join(UPLOAD_ROOT, relativePath.replace("uploads/", ""));


  if (!require("fs").existsSync(absImagePath)) {
    throw new Error("Image not found: " + absImagePath);
  }

  const classifyRes = await axios.post(`${ML_BASE_URL}/classify`, {
    image_path: absImagePath
  });

  const { label, confidence } = classifyRes.data;

  const embedRes = await axios.post(`${ML_BASE_URL}/embed`, {
    image_path: absImagePath
  });

  const { embedding_path } = embedRes.data;

  const [cats] = await pool.execute(
    "SELECT id FROM categories WHERE code = ?",
    [label]
  );

  const categoryId = cats.length ? cats[0].id : null;

  const [result] = await pool.execute(
    `
    INSERT INTO wardrobe_items
    (user_id, category_id, image_path, embedding_path, ai_label, confidence)
    VALUES (?, ?, ?, ?, ?, ?)
    `,
    [userId, categoryId, relativePath, embedding_path, label, confidence]
  );

  return { id: result.insertId, label, confidence };
};

/**
 * Get wardrobe
 */
exports.getItems = async (userId, category) => {
  let sql = `
    SELECT *
    FROM wardrobe_items
    WHERE user_id = ?
      AND is_deleted = FALSE
  `;
  const params = [userId];

  if (category) {
    sql += " AND ai_label = ?";
    params.push(category);
  }

  const [rows] = await pool.execute(sql, params);
  return rows;
};

/**
 * Update label
 */
exports.updateLabel = async (itemId, userId, userLabel) => {
  await pool.execute(
    `
    UPDATE wardrobe_items
    SET user_label = ?
    WHERE id = ? AND user_id = ?
    `,
    [userLabel, itemId, userId]
  );
};
