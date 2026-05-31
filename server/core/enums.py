"""全局枚举定义。

这些短码必须和 `docs/数据模型规格.md` 第 2 节保持一致。
"""

from enum import StrEnum


class LearningState(StrEnum):
    """学生当前学习/情绪状态，写入 `learning_event.state`。"""

    STABLE = "stable"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    TIRED = "tired"
    ANXIOUS = "anxious"


class TeachingStrategy(StrEnum):
    """教学编排器可组合使用的教学策略。"""

    SOCRATIC = "socratic"
    SMALL_STEP = "small_step"
    HINT = "hint"
    CARE = "care"
    HUMOR = "humor"
    DIRECT_EXPLAIN = "direct_explain"


class ErrorCause(StrEnum):
    """深图模块归因出的错因分类。"""

    CALCULATION = "calculation"
    CONCEPT = "concept"
    MISREAD = "misread"
    METHOD = "method"
    INCOMPLETE = "incomplete"
    CARELESS = "careless"
    UNKNOWN = "unknown"


class VisualAidType(StrEnum):
    """本轮实际使用的视觉辅助类型。"""

    NONE = "none"
    FUNCTION_GRAPH = "function_graph"
    GEOMETRY = "geometry"
    ANNOTATION = "annotation"
    DIAGRAM = "diagram"


class Difficulty(StrEnum):
    """题目难度枚举。"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ReviewStatus(StrEnum):
    """复习任务状态枚举。"""

    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"


class LlmMode(StrEnum):
    """LLM 运行模式，mock 用于离线演示，live 用于真实模型调用。"""

    MOCK = "mock"
    LIVE = "live"
