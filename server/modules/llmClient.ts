import type {
  EmotionRecognitionRequest,
  EmotionRecognitionResponse,
  GenerateResponseRequest,
  GenerateResponseResponse,
  LearningState
} from "../../shared/api.js";

export type LlmMode = "mock" | "live";

export interface LlmClient {
  recognizeEmotion(input: EmotionRecognitionRequest): Promise<EmotionRecognitionResponse>;
  generateResponse(input: GenerateResponseRequest): Promise<GenerateResponseResponse>;
}

export function getLlmMode(): LlmMode {
  return process.env.LLM_MODE === "live" ? "live" : "mock";
}

export function createLlmClient(mode = getLlmMode()): LlmClient {
  if (mode === "live") {
    return liveClient;
  }

  return mockClient;
}

export async function recognizeEmotion(
  input: EmotionRecognitionRequest
): Promise<EmotionRecognitionResponse> {
  return createLlmClient().recognizeEmotion(input);
}

export async function generateResponse(
  input: GenerateResponseRequest
): Promise<GenerateResponseResponse> {
  return createLlmClient().generateResponse(input);
}

const mockClient: LlmClient = {
  async recognizeEmotion(input) {
    return recognizeEmotionMock(input);
  },

  async generateResponse(input) {
    return generateResponseMock(input);
  }
};

const liveClient: LlmClient = {
  async recognizeEmotion() {
    throw new Error("LLM_MODE=live is not implemented yet. Use LLM_MODE=mock for T1-2.");
  },

  async generateResponse() {
    throw new Error("LLM_MODE=live is not implemented yet. Use LLM_MODE=mock for T1-2.");
  }
};

function recognizeEmotionMock(input: EmotionRecognitionRequest): EmotionRecognitionResponse {
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

function generateResponseMock(input: GenerateResponseRequest): GenerateResponseResponse {
  if (input.careTriggered || input.strategy.includes("care")) {
    return {
      tutor_response:
        "先别急，这一步卡住很正常。我们把题目拆小一点：先看你现在最确定的条件是哪一个？"
    };
  }

  if (input.strategy.includes("small_step")) {
    return {
      tutor_response: "我们只往前走一步：先把题目里的关键条件圈出来，再判断它能推出什么。"
    };
  }

  if (input.strategy.includes("hint")) {
    return {
      tutor_response: "给你一个小提示：先别急着算结果，看看这个条件对应的是哪个知识点。"
    };
  }

  if (input.strategy.includes("direct_explain")) {
    return {
      tutor_response: "这题的关键是先确定方法，再代入计算。我先把第一步讲清楚：从已知条件建立关系式。"
    };
  }

  return {
    tutor_response: "我们先从你已经确定的一步开始。你觉得题目里最有用的信息是哪一句？"
  };
}
