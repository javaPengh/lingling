"""全局配置读取。

配置来源优先使用环境变量，同时兼容根目录 `.env` 和 `server/.env`。
本文件不保存密钥，只读取运行时注入的值。
"""

from dataclasses import dataclass
from pathlib import Path
import os


ROOT_DIR = Path(__file__).resolve().parents[2]
SERVER_DIR = ROOT_DIR / "server"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(ROOT_DIR / ".env")
_load_env_file(SERVER_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """后端运行配置快照。"""

    port: int = int(os.environ.get("PORT", "3001"))
    web_origin: str = os.environ.get("WEB_ORIGIN", "http://localhost:5173")
    llm_mode: str = os.environ.get("LLM_MODE", "mock")
    llm_provider: str = os.environ.get("LLM_PROVIDER", "deepseek")
    llm_api_base_url: str = (
        os.environ.get("LLM_API_BASE_URL")
        or os.environ.get("DEEPSEEK_API_BASE_URL")
        or "https://api.deepseek.com"
    )
    llm_api_key: str = os.environ.get("LLM_API_KEY") or os.environ.get("DEEPSEEK_API_KEY", "")
    llm_model: str = os.environ.get("LLM_MODEL", "deepseek-chat")
    llm_timeout_seconds: float = float(os.environ.get("LLM_TIMEOUT_SECONDS", "3"))
    database_path: Path = Path(os.environ.get("DATABASE_PATH", str(ROOT_DIR / "lingling.db")))


settings = Settings()
