"""全局枚举定义。

这些短码必须和 `docs/数据模型规格.md` 第 2 节保持一致。
"""

from enum import StrEnum


class LearningState(StrEnum):
    """学生当前学习/情绪状态，写入 `learning_event.state`。"""

    # 状态稳定，能正常跟随当前学习节奏。
    STABLE = "stable"
    # 表达困惑、卡住或首次作答错误，但尚未明显受挫。
    CONFUSED = "confused"
    # 连续受阻、放弃倾向或自我否定，优先触发关怀。
    FRUSTRATED = "frustrated"
    # 注意力下降或明确表达疲惫，需要缩短任务或建议休息。
    TIRED = "tired"
    # 对考试、时间或结果明显担忧，需要先安抚再推进。
    ANXIOUS = "anxious"


class TeachingStrategy(StrEnum):
    """教学编排器可组合使用的教学策略。"""

    # 苏格拉底式追问，引导学生自己说出关键推理。
    SOCRATIC = "socratic"
    # 拆小步引导，把当前题目压到最小可完成步骤。
    SMALL_STEP = "small_step"
    # 给提示但不直接给完整答案。
    HINT = "hint"
    # 主动关怀，先处理情绪再回到题目。
    CARE = "care"
    # 轻度幽默，用于降压但不喧宾夺主。
    HUMOR = "humor"
    # 直接讲解兜底，仅在启发无效或学生明确放弃时使用。
    DIRECT_EXPLAIN = "direct_explain"


class ErrorCause(StrEnum):
    """深图模块归因出的错因分类。"""

    # 计算过程出错。
    CALCULATION = "calculation"
    # 概念理解或知识点关系判断出错。
    CONCEPT = "concept"
    # 审题误读、漏看条件或误解题意。
    MISREAD = "misread"
    # 方法选择不当或解题路径不合适。
    METHOD = "method"
    # 分类讨论、步骤或答案不完整。
    INCOMPLETE = "incomplete"
    # 粗心导致的端点、符号、抄写等错误。
    CARELESS = "careless"
    # 暂时无法可靠归因。
    UNKNOWN = "unknown"


class VisualAidType(StrEnum):
    """本轮实际使用的视觉辅助类型。"""

    # 不使用视觉辅助。
    NONE = "none"
    # 函数图像辅助。
    FUNCTION_GRAPH = "function_graph"
    # 几何/立体几何图形辅助。
    GEOMETRY = "geometry"
    # 在已有图或题目上做标注、高亮、辅助线。
    ANNOTATION = "annotation"
    # 通用示意图或流程图辅助。
    DIAGRAM = "diagram"


class Difficulty(StrEnum):
    """题目难度枚举。"""

    # 简单题，用于热身或基础确认。
    EASY = "easy"
    # 中等题，用于常规练习。
    MEDIUM = "medium"
    # 较难题，用于演示受阻、拆步和关怀链路。
    HARD = "hard"


class ReviewStatus(StrEnum):
    """复习任务状态枚举。"""

    # 待完成。
    PENDING = "pending"
    # 已完成。
    DONE = "done"
    # 已跳过。
    SKIPPED = "skipped"


class LlmMode(StrEnum):
    """LLM 运行模式，mock 用于离线演示，live 用于真实模型调用。"""

    # 离线 mock 模式，用于本地开发和演示兜底。
    MOCK = "mock"
    # 真实模型模式，通过后端环境变量调用外部 LLM。
    LIVE = "live"
