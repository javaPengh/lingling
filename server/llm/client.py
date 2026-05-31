from functools import lru_cache

from server.core.config import settings
from server.llm.base import LlmClient
from server.llm.deepseek_client import DeepSeekClient
from server.llm.mock_client import MockLlmClient


@lru_cache(maxsize=1)
def get_llm_client() -> LlmClient:
    if settings.llm_mode == "live":
        return DeepSeekClient()
    return MockLlmClient()
