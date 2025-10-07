const express = require("express");
const app = express();
const port = 8002;

app.get("/api/keep-active", (req, res) => {
  res.send({ status: "Server is active" });
});

app.listen(port, () => {
  console.log(`Express app listening at http://localhost:${port}`);
});
