"""LLM 客户端工厂。

根据 `LLM_MODE` 选择 mock 或真实模型客户端，并缓存实例。
"""

from functools import lru_cache

from server.core.config import settings
from server.llm.base import LlmClient
from server.llm.deepseek_client import DeepSeekClient
from server.llm.mock_client import MockLlmClient


@lru_cache(maxsize=1)
def get_llm_client() -> LlmClient:
    """返回当前配置下的 LLM 客户端。"""

    if settings.llm_mode == "live":
        return DeepSeekClient()
    return MockLlmClient()
