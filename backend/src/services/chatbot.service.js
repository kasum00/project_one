const pool = require("../config/database");
const axios = require("axios");

const ML_URL = "http://localhost:8000";

// =================================================
// 🅰️ FIND SIMILAR ITEM
// Trả về item cùng ai_label trong wardrobe user
// =================================================
exports.findSimilarItem = async (userId, itemId) => {
  // 1️⃣ Query item
  const [[query]] = await pool.execute(
    `
    SELECT id, image_path, embedding_path, ai_label
    FROM wardrobe_items
    WHERE id = ? AND user_id = ? AND is_deleted = FALSE
    `,
    [itemId, userId]
  );

  if (!query) throw new Error("Item not found");

  // 2️⃣ Gọi ML để lấy similarity (global, chỉ để lấy score)
  const recRes = await axios.post(`${ML_URL}/recommend`, {
    embedding_path: query.embedding_path,
    top_k: 50
  });

  const similarities = recRes.data || [];

  // 3️⃣ Lấy wardrobe cùng ai_label
  const [items] = await pool.execute(
    `
    SELECT id, image_path, embedding_path, ai_label
    FROM wardrobe_items
    WHERE user_id = ?
      AND ai_label = ?
      AND id != ?
      AND is_deleted = FALSE
    `,
    [userId, query.ai_label, itemId]
  );

  if (!items.length) return [];

  // 4️⃣ Gán similarity theo thứ tự (ML không biết wardrobe)
  return items.slice(0, 5).map((it, idx) => ({
    ...it,
    similarity: similarities[idx]?.similarity ?? 0
  }));
};


// =================================================
// 🅱️ FIND MATCHING OUTFIT (FULL OUTFIT)
// Query item + top / bottom / shoes / bag ...
// =================================================
exports.findMatchingOutfit = async (userId, itemId) => {
  // 1️⃣ Query item
  const [[query]] = await pool.execute(
    `
    SELECT id, image_path, embedding_path, ai_label
    FROM wardrobe_items
    WHERE id = ? AND user_id = ? AND is_deleted = FALSE
    `,
    [itemId, userId]
  );

  if (!query) throw new Error("Item not found");

  // 2️⃣ Fashion rules
  const targetGroups = getTargetGroups(query.ai_label);

  // 3️⃣ Lấy toàn bộ wardrobe user (trừ query)
  const [items] = await pool.execute(
    `
    SELECT id, image_path, embedding_path, ai_label
    FROM wardrobe_items
    WHERE user_id = ?
      AND id != ?
      AND is_deleted = FALSE
    `,
    [userId, itemId]
  );

  if (!items.length) {
    return [{ ...query, role: "query" }];
  }

  // 4️⃣ Group theo ai_label
  const grouped = {};
  for (const it of items) {
    grouped[it.ai_label] ??= [];
    grouped[it.ai_label].push(it);
  }

  // 5️⃣ Build FULL outfit (LUÔN BAO GỒM QUERY)
  const outfit = [
    {
      ...query,
      role: "query"
    }
  ];

  for (const group of targetGroups) {
    if (!grouped[group]?.length) continue;

    const arr = grouped[group];
    const chosen = arr[Math.floor(Math.random() * arr.length)];

    outfit.push({
      ...chosen,
      role: group
    });
  }

  return outfit;
};


// =================================================
// 👗 FASHION RULES (JS VERSION – ĐƠN GIẢN, CHẮC)
// =================================================
function getTargetGroups(cat) {
  const TOPS = new Set(["tops", "top"]);
  const BOTTOMS = new Set(["bottoms", "pants", "skirt"]);
  const ONEPIECE = new Set(["dress", "jumpsuit"]);
  const SHOES = "shoes";
  const BAG = "bag";
  const ACCESSORIES = "accessories";
  const OUTWEAR = "outwear";

  // Dress / jumpsuit
  if (ONEPIECE.has(cat)) {
    return [SHOES, BAG, ACCESSORIES];
  }

  // Top
  if (TOPS.has(cat)) {
    return ["bottoms", SHOES, BAG];
  }

  // Bottom
  if (BOTTOMS.has(cat)) {
    return ["tops", SHOES, BAG];
  }

  // Shoes
  if (cat === SHOES) {
    return ["tops", "bottoms", BAG];
  }

  // Bag / accessories
  if (cat === BAG || cat === ACCESSORIES) {
    return ["tops", "bottoms", SHOES];
  }

  // Fallback
  return ["tops", "bottoms", SHOES];
}
