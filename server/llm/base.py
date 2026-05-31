"""LLM 适配层抽象接口。

业务层只依赖这里定义的能力，不关心底层是 mock 还是 DeepSeek。
"""

from abc import ABC, abstractmethod

from server.models.schemas import (
    EmotionRecognitionInput,
    EmotionRecognitionResult,
    GenerateResponseInput,
    GenerateResponseResult,
)


class LlmError(RuntimeError):
    """LLM 调用失败或返回内容不合规时抛出的统一异常。"""

    pass


class LlmClient(ABC):
    """大模型客户端统一接口。"""

    @abstractmethod
    def recognize_emotion(self, payload: EmotionRecognitionInput) -> EmotionRecognitionResult:
        """识别学生当前学习状态。"""

        raise NotImplementedError

    @abstractmethod
    def generate_response(self, payload: GenerateResponseInput) -> GenerateResponseResult:
        """根据编排结果生成灵灵给学生的回复。"""

        raise NotImplementedError
