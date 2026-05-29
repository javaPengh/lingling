import type {
  EmotionRecognitionRequest,
  EmotionRecognitionResponse,
  LearningState
} from "../../../shared/api.js";

export function recognizeEmotionMock(
  input: EmotionRecognitionRequest
): EmotionRecognitionResponse {
  const text = input.studentInput.trim();
  const highSignal = input.ruleSignals?.find((signal) => signal.severity === "high");
  const state = pickMockState(text, input.isCorrect ?? null, Boolean(highSignal));

  return {
    state,
    confidence: mockConfidenceForState(state),
    evidence: buildMockEvidence(text, state, input, highSignal?.description)
  };
}

function pickMockState(
  text: string,
  isCorrect: boolean | null,
  hasHighSignal: boolean
): LearningState {
  if (/来不及|考试|紧张|焦虑|完蛋/.test(text)) {
    return "anxious";
  }

  if (/困|累|不想|没精神|随便/.test(text)) {
    return "tired";
  }

  if (/不会|算了|不学了|我不行|太难|崩溃/.test(text) || hasHighSignal) {
    return "frustrated";
  }

  if (/为什么|怎么|哪一步|看不懂|不明白|卡住/.test(text) || isCorrect === false) {
    return "confused";
  }

  return "stable";
}

function mockConfidenceForState(state: LearningState): number {
  const confidenceByState: Record<LearningState, number> = {
    stable: 0.72,
    confused: 0.81,
    frustrated: 0.88,
    tired: 0.76,
    anxious: 0.84
  };

  return confidenceByState[state];
}

function buildMockEvidence(
  text: string,
  state: LearningState,
  input: EmotionRecognitionRequest,
  highSignal?: string
): string {
  if (highSignal) {
    return `mock：命中高强度规则信号“${highSignal}”，并结合学生原话“${text || "空输入"}”，判为 ${state}。`;
  }

  if (input.isCorrect === false) {
    return `mock：本轮作答错误，学生原话“${text || "空输入"}”，仍在尝试但出现卡顿，判为 ${state}。`;
  }

  if (input.ruleSignals?.length) {
    return `mock：结合规则信号“${input.ruleSignals[0]?.description}”和学生原话“${text || "空输入"}”，判为 ${state}。`;
  }

  return `mock：根据学生原话“${text || "空输入"}”的语气与关键词，判为 ${state}。`;
}
