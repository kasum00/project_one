const express = require("express");
const jwt = require("jsonwebtoken");
const router = express.Router();

router.post("/login", (req, res) => {
  const { email, password } = req.body;

  // TEST CỨNG – KHỎI DB
  if (email !== "test@gmail.com" || password !== "123456") {
    return res.status(401).json({ message: "Wrong credentials" });
  }

  const token = jwt.sign(
    {
      id: 1,
      email: "test@gmail.com",
      full_name: "Test User",
    },
    "SECRET_KEY_123",
    { expiresIn: "1h" }
  );

  res.json({ token });
});

module.exports = router;
