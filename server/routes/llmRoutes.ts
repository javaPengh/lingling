import { Router } from "express";
import type {
  EmotionRecognitionRequest,
  GenerateResponseRequest,
  LearningState,
  TeachingStrategy,
  VisualAidType
} from "../../shared/api.js";
import { generateResponse, recognizeEmotion } from "../modules/llmClient.js";

export const llmRouter = Router();

llmRouter.post("/recognize-emotion", async (req, res, next) => {
  try {
    if (!isEmotionRecognitionRequest(req.body)) {
      res.status(400).json({ error: "bad_request", message: "studentInput is required." });
      return;
    }

    const body = req.body;
    const result = await recognizeEmotion(body);

    res.json(result);
  } catch (error) {
    next(error);
  }
});

llmRouter.post("/generate-response", async (req, res, next) => {
  try {
    if (!isGenerateResponseRequest(req.body)) {
      res.status(400).json({
        error: "bad_request",
        message: "state, strategy, careTriggered, visualAidUsed and studentInput are required."
      });
      return;
    }

    const body = req.body;
    const result = await generateResponse(body);

    res.json(result);
  } catch (error) {
    next(error);
  }
});

const learningStates: readonly LearningState[] = [
  "stable",
  "confused",
  "frustrated",
  "tired",
  "anxious"
];

const teachingStrategies: readonly TeachingStrategy[] = [
  "socratic",
  "small_step",
  "hint",
  "care",
  "humor",
  "direct_explain"
];

const visualAidTypes: readonly VisualAidType[] = [
  "none",
  "function_graph",
  "geometry",
  "annotation",
  "diagram"
];

function isEmotionRecognitionRequest(value: unknown): value is EmotionRecognitionRequest {
  const body = value as Partial<EmotionRecognitionRequest>;

  return typeof body?.studentInput === "string";
}

function isGenerateResponseRequest(value: unknown): value is GenerateResponseRequest {
  const body = value as Partial<GenerateResponseRequest>;

  return (
    typeof body?.studentInput === "string" &&
    typeof body.careTriggered === "boolean" &&
    isOneOf(body.state, learningStates) &&
    isOneOf(body.visualAidUsed, visualAidTypes) &&
    Array.isArray(body.strategy) &&
    body.strategy.every((strategy) => isOneOf(strategy, teachingStrategies))
  );
}

function isOneOf<T extends string>(value: unknown, options: readonly T[]): value is T {
  return typeof value === "string" && options.includes(value as T);
}
