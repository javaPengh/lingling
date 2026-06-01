"""账号密码哈希工具。

V0.1 使用预置账号密码登录，本文件提供最小的 PBKDF2 哈希与校验能力。
"""

from __future__ import annotations

import base64
import hashlib
import secrets


PASSWORD_HASH_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_ITERATIONS = 120_000


def hash_password(password: str, salt: str | None = None) -> str:
    """把明文密码转换为可存储的 PBKDF2-SHA256 哈希字符串。"""

    salt_bytes = salt.encode("utf-8") if salt is not None else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PASSWORD_HASH_ITERATIONS,
    )
    salt_text = base64.urlsafe_b64encode(salt_bytes).decode("ascii")
    digest_text = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"{PASSWORD_HASH_ALGORITHM}${PASSWORD_HASH_ITERATIONS}${salt_text}${digest_text}"


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码是否匹配已存储的 PBKDF2-SHA256 哈希。"""

    try:
        algorithm, iterations_text, salt_text, expected_text = password_hash.split("$", 3)
        if algorithm != PASSWORD_HASH_ALGORITHM:
            return False
        iterations = int(iterations_text)
        salt_bytes = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(expected_text.encode("ascii"))
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
    return secrets.compare_digest(actual, expected)
