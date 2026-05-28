import assert from "node:assert/strict";
import { createLlmClient } from "../modules/llmClient.js";

const llm = createLlmClient("mock");

const emotion = await llm.recognizeEmotion({
  studentInput: "我不会，算了吧，这题太难了",
  isCorrect: false,
  knowledgePointIds: ["kp_001"],
  ruleSignals: [
    {
      code: "consecutive_wrong",
      description: "同一知识点连续答错 2 次",
      severity: "high"
    }
  ],
  historySummary: "近期遇到函数题容易挫败。",
  recentTurns: ["学生答错一次", "学生回复变短"]
});

assert.equal(emotion.state, "frustrated");
assert.equal(typeof emotion.confidence, "number");
assert.ok(emotion.confidence >= 0 && emotion.confidence <= 1);
assert.ok(emotion.evidence.length > 0);

const response = await llm.generateResponse({
  state: emotion.state,
  strategy: ["care", "small_step"],
  careTriggered: true,
  visualAidUsed: "none",
  studentInput: "我不会，算了吧，这题太难了",
  isCorrect: false,
  errorCause: "concept",
  errorDetail: "没有识别二次函数顶点。"
});

assert.equal(typeof response.tutor_response, "string");
assert.ok(response.tutor_response.length > 0);

console.log(
  JSON.stringify(
    {
      recognizeEmotion: emotion,
      generateResponse: response
    },
    null,
    2
  )
);
