import cors from "cors";
import express, { type ErrorRequestHandler } from "express";
import { apiRouter } from "./routes/index.js";

const webOrigin = process.env.WEB_ORIGIN ?? "http://localhost:5173";

export const app = express();

app.use(cors({ origin: webOrigin }));
app.use(express.json());

app.use("/api", apiRouter);

app.use((_req, res) => {
  res.status(404).json({ error: "not_found" });
});

const errorHandler: ErrorRequestHandler = (error, _req, res, _next) => {
  console.error(error);

  res.status(500).json({
    error: "internal_error",
    message: error instanceof Error ? error.message : "Unexpected server error"
  });
};

app.use(errorHandler);
