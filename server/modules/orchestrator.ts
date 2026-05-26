import type { LearningTurnRequest, LearningTurnResponse } from "../../shared/api.js";

export async function orchestrateTurn(input: LearningTurnRequest): Promise<LearningTurnResponse> {
  return {
    eventId: `evt_${Date.now()}`,
    state: "stable",
    stateEvidence: "mock skeleton response",
    strategy: ["socratic"],
    strategyReason: "default skeleton strategy",
    careTriggered: false,
    visualAidUsed: "none",
    tutorResponse: input.studentInput ? "我们先把这一句里确定的信息圈出来。" : "今天先从一道小题热身。"
  };
}
