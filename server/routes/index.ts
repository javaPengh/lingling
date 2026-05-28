import { Router } from "express";
import type { HealthResponse, StudentsListResponse } from "../../shared/api.js";
import { listStudents } from "../db/index.js";
import { llmRouter } from "./llmRoutes.js";

export const apiRouter = Router();

apiRouter.use("/llm", llmRouter);

apiRouter.get("/health", (_req, res) => {
  const body: HealthResponse = {
    ok: true,
    service: "lingling-server",
    mode: process.env.LLM_MODE === "live" ? "live" : "mock"
  };

  res.json(body);
});

apiRouter.get("/students", (_req, res, next) => {
  try {
    const body: StudentsListResponse = {
      students: listStudents()
    };

    res.json(body);
  } catch (error) {
    next(error);
  }
});
