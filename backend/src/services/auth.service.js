const bcrypt = require("bcryptjs");
const pool = require("../config/database");
const { signToken } = require("../utils/jwt");

exports.signup = async ({ email, password, fullName }) => {
  const hashedPassword = await bcrypt.hash(password, 10);

  const [result] = await pool.execute(
    "INSERT INTO users (email, password, full_name) VALUES (?, ?, ?)",
    [email, hashedPassword, fullName]
  );

  await pool.execute(
    "INSERT INTO user_profiles (user_id) VALUES (?)",
    [result.insertId]
  );

  return { id: result.insertId, email, fullName };
};

exports.login = async ({ email, password }) => {
  const [rows] = await pool.execute(
    "SELECT * FROM users WHERE email = ?",
    [email]
  );

  if (rows.length === 0) {
    throw new Error("Email không tồn tại");
  }

  const user = rows[0];
  const isMatch = await bcrypt.compare(password, user.password);

  if (!isMatch) {
    throw new Error("Sai mật khẩu");
  }

  const token = signToken({ id: user.id, email: user.email });

  return {
    token,
    user: {
      id: user.id,
      email: user.email,
      fullName: user.full_name,
    },
  };
};
