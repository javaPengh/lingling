import type {
  EmotionRecognitionRequest,
  EmotionRecognitionResponse,
  GenerateResponseRequest,
  GenerateResponseResponse
} from "../../../shared/api.js";

/** 大模型运行模式：mock 用于本地开发和演示兜底，live 预留给真实模型接入。 */
export type LlmMode = "mock" | "live";

/** 业务层只依赖这个接口，不关心背后是 mock 还是真实模型厂商。 */
export interface LlmClient {
  /** 根据学生输入、规则信号和历史摘要识别本轮学习状态。 */
  recognizeEmotion(input: EmotionRecognitionRequest): Promise<EmotionRecognitionResponse>;

  /** 根据编排器选定的状态、策略和题目信息生成灵灵回复。 */
  generateResponse(input: GenerateResponseRequest): Promise<GenerateResponseResponse>;
}
