from abc import ABC, abstractmethod

from server.models.schemas import (
    EmotionRecognitionInput,
    EmotionRecognitionResult,
    GenerateResponseInput,
    GenerateResponseResult,
)


class LlmError(RuntimeError):
    pass


class LlmClient(ABC):
    @abstractmethod
    def recognize_emotion(self, payload: EmotionRecognitionInput) -> EmotionRecognitionResult:
        raise NotImplementedError

    @abstractmethod
    def generate_response(self, payload: GenerateResponseInput) -> GenerateResponseResult:
        raise NotImplementedError
