import assert from "node:assert/strict";
import type { AddressInfo } from "node:net";
import { app } from "../app.js";

const server = app.listen(0);

try {
  await new Promise<void>((resolve) => {
    server.once("listening", resolve);
  });

  const { port } = server.address() as AddressInfo;
  const baseUrl = `http://127.0.0.1:${port}/api/llm`;

  const emotionResponse = await postJson(`${baseUrl}/recognize-emotion`, {
    studentInput: "我不会，算了吧，这题太难了",
    isCorrect: false,
    ruleSignals: [
      {
        code: "consecutive_wrong",
        description: "同一知识点连续答错 2 次",
        severity: "high"
      }
    ]
  });

  assert.equal(emotionResponse.status, 200);
  assert.equal(emotionResponse.body.state, "frustrated");
  assert.equal(typeof emotionResponse.body.confidence, "number");
  assert.equal(typeof emotionResponse.body.evidence, "string");

  const tutorResponse = await postJson(`${baseUrl}/generate-response`, {
    state: "frustrated",
    strategy: ["care", "small_step"],
    careTriggered: true,
    visualAidUsed: "none",
    studentInput: "我不会，算了吧，这题太难了",
    isCorrect: false
  });

  assert.equal(tutorResponse.status, 200);
  const tutorResponseText = tutorResponse.body.tutor_response;
  if (typeof tutorResponseText !== "string") {
    throw new Error("Expected tutor_response to be a string.");
  }
  assert.ok(tutorResponseText.length > 0);

  const badRequest = await postJson(`${baseUrl}/recognize-emotion`, {});
  assert.equal(badRequest.status, 400);
  assert.equal(badRequest.body.error, "bad_request");

  console.log(
    JSON.stringify(
      {
        recognizeEmotion: emotionResponse.body,
        generateResponse: tutorResponse.body,
        badRequest: badRequest.body
      },
      null,
      2
    )
  );
} finally {
  await new Promise<void>((resolve, reject) => {
    server.close((error) => {
      if (error) {
        reject(error);
        return;
      }

      resolve();
    });
  });
}

async function postJson(url: string, body: unknown) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });

  return {
    status: response.status,
    body: (await response.json()) as Record<string, unknown>
  };
}
