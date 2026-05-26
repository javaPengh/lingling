import "dotenv/config";
import cors from "cors";
import express from "express";
import { apiRouter } from "./routes/index.js";

const app = express();
const port = Number(process.env.PORT ?? 3001);
const webOrigin = process.env.WEB_ORIGIN ?? "http://localhost:5173";

app.use(cors({ origin: webOrigin }));
app.use(express.json());

app.use("/api", apiRouter);

app.use((_req, res) => {
  res.status(404).json({ error: "not_found" });
});

app.listen(port, () => {
  console.log(`Lingling server listening on http://localhost:${port}`);
});
