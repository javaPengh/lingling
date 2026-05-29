import type { LlmClient } from "./types.js";

/** 真实模型适配器占位。阶段四接国内大模型时，只替换这一层。 */
export const liveClient: LlmClient = {
  async recognizeEmotion() {
    throw new Error("LLM_MODE=live is not implemented yet. Use LLM_MODE=mock for T1-2.");
  },

  async generateResponse() {
    throw new Error("LLM_MODE=live is not implemented yet. Use LLM_MODE=mock for T1-2.");
  }
};
