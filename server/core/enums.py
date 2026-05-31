from enum import StrEnum


class LearningState(StrEnum):
    STABLE = "stable"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    TIRED = "tired"
    ANXIOUS = "anxious"


class TeachingStrategy(StrEnum):
    SOCRATIC = "socratic"
    SMALL_STEP = "small_step"
    HINT = "hint"
    CARE = "care"
    HUMOR = "humor"
    DIRECT_EXPLAIN = "direct_explain"


class ErrorCause(StrEnum):
    CALCULATION = "calculation"
    CONCEPT = "concept"
    MISREAD = "misread"
    METHOD = "method"
    INCOMPLETE = "incomplete"
    CARELESS = "careless"
    UNKNOWN = "unknown"


class VisualAidType(StrEnum):
    NONE = "none"
    FUNCTION_GRAPH = "function_graph"
    GEOMETRY = "geometry"
    ANNOTATION = "annotation"
    DIAGRAM = "diagram"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"
    SKIPPED = "skipped"


class LlmMode(StrEnum):
    MOCK = "mock"
    LIVE = "live"
