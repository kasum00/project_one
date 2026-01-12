const authService = require("../services/auth.service");

exports.signup = async (req, res) => {
  try {
    const { email, password, fullName } = req.body;
    const user = await authService.signup({ email, password, fullName });
    res.status(201).json({ success: true, user });
  } catch (err) {
    res.status(400).json({ success: false, message: err.message });
  }
};

exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;
    const data = await authService.login({ email, password });
    res.json({ success: true, ...data });
  } catch (err) {
    res.status(401).json({ success: false, message: err.message });
  }
};
