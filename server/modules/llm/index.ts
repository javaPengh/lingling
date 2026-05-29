import type {
  EmotionRecognitionRequest,
  EmotionRecognitionResponse,
  GenerateResponseRequest,
  GenerateResponseResponse
} from "../../../shared/api.js";
import { liveClient } from "./liveClient.js";
import { mockClient } from "./mockClient.js";
import type { LlmClient, LlmMode } from "./types.js";

export type { LlmClient, LlmMode } from "./types.js";

/** 读取后端环境变量中的 LLM_MODE，默认走 mock，避免无密钥时启动失败。 */
export function getLlmMode(): LlmMode {
  return process.env.LLM_MODE === "live" ? "live" : "mock";
}

/** 创建当前模式的大模型客户端。业务代码通过 LlmClient 接口调用即可。 */
export function createLlmClient(mode = getLlmMode()): LlmClient {
  if (mode === "live") {
    return liveClient;
  }

  return mockClient;
}

/** 对外门面：识别本轮学生学习状态。 */
export async function recognizeEmotion(
  input: EmotionRecognitionRequest
): Promise<EmotionRecognitionResponse> {
  return createLlmClient().recognizeEmotion(input);
}

/** 对外门面：生成灵灵本轮教学回复。 */
export async function generateResponse(
  input: GenerateResponseRequest
): Promise<GenerateResponseResponse> {
  return createLlmClient().generateResponse(input);
}
