import { recognizeEmotionMock } from "./mockEmotion.js";
import { generateResponseMock } from "./mockResponse.js";
import type { LlmClient } from "./types.js";

/** T1-2 使用的离线 mock client，保证无模型密钥时也能跑通验收。 */
export const mockClient: LlmClient = {
  async recognizeEmotion(input) {
    return recognizeEmotionMock(input);
  },

  async generateResponse(input) {
    return generateResponseMock(input);
  }
};
