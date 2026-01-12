const express = require("express");
const cors = require("cors");
const path = require("path");


const authRoutes = require("./routes/auth.routes");
const userRoutes = require("./routes/user.routes");
const chatbotRoutes = require("./routes/chatbot.routes");

const recommendRoutes = require("./routes/recommend.routes");




const app = express();

app.use(cors());
app.use(express.json());

app.use(
  "/uploads",
  express.static(path.join(__dirname, "./uploads"))
);
app.use("/api/auth", authRoutes);
app.use("/api/users", userRoutes);
const wardrobeRoutes = require("./routes/wardrobe.routes");

app.use("/api/wardrobe", wardrobeRoutes);

app.use("/api/chatbot", chatbotRoutes);
app.use("/api/recommend", recommendRoutes);
module.exports = app;
