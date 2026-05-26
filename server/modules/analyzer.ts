import type { ErrorCause } from "../../shared/api.js";

export interface AnalysisResult {
  isCorrect: boolean | null;
  knowledgePointIds: string[];
  errorCause: ErrorCause | null;
  errorDetail: string | null;
}

export async function analyzeTurn(): Promise<AnalysisResult> {
  return {
    isCorrect: null,
    knowledgePointIds: [],
    errorCause: null,
    errorDetail: null
  };
}
