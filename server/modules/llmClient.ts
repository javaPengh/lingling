import type { LearningState } from "../../shared/api.js";

export interface EmotionRecognitionResult {
  state: LearningState;
  confidence: number;
  evidence: string;
}

export async function recognizeEmotion(): Promise<EmotionRecognitionResult> {
  return {
    state: "stable",
    confidence: 0.5,
    evidence: "mock mode placeholder"
  };
}

export async function generateResponse(): Promise<string> {
  return "我们先从你已经确定的一步开始。";
}
