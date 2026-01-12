const app = require("./app");
require("dotenv").config();

app.listen(process.env.PORT, () => {
  console.log(` Backend chạy tại http://localhost:${process.env.PORT}`);
});
