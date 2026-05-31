"""DeepSeek 真实模型客户端。

通过 OpenAI-compatible Chat Completions API 调用 DeepSeek，密钥只从环境变量读取。
"""

import json

import httpx

from server.core.config import settings
from server.llm.base import LlmClient, LlmError
from server.llm.prompts.emotion import EMOTION_SYSTEM_PROMPT
from server.llm.prompts.teaching import TEACHING_SYSTEM_PROMPT
from server.models.schemas import (
    EmotionRecognitionInput,
    EmotionRecognitionResult,
    GenerateResponseInput,
    GenerateResponseResult,
)


class DeepSeekClient(LlmClient):
    """DeepSeek live 模式适配器。"""

    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise LlmError("Missing DeepSeek API key")
        self.base_url = settings.llm_api_base_url.rstrip("/")
        self.model = settings.llm_model
        self.timeout = settings.llm_timeout_seconds
        self.headers = {
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        }

    def recognize_emotion(self, payload: EmotionRecognitionInput) -> EmotionRecognitionResult:
        """调用 DeepSeek 完成情绪识别，并校验 JSON 输出。"""

        content = self._chat(
            EMOTION_SYSTEM_PROMPT,
            json.dumps(payload.model_dump(by_alias=True), ensure_ascii=False),
        )
        try:
            data = json.loads(content)
            return EmotionRecognitionResult.model_validate(data)
        except Exception as exc:
            raise LlmError(f"Invalid emotion JSON from DeepSeek: {content}") from exc

    def generate_response(self, payload: GenerateResponseInput) -> GenerateResponseResult:
        """调用 DeepSeek 生成灵灵教学回应。"""

        content = self._chat(
            TEACHING_SYSTEM_PROMPT,
            json.dumps(payload.model_dump(by_alias=True), ensure_ascii=False),
        )
        return GenerateResponseResult(tutor_response=content.strip())

    def _chat(self, system_prompt: str, user_prompt: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.base_url}/chat/completions", headers=self.headers, json=body)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            raise LlmError("DeepSeek request failed") from exc
