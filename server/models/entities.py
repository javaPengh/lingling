"""数据库实体模型。

本文件只描述系统内部的核心领域对象，以及它们和 SQLite 表结构的对应关系。
字段命名保持 snake_case，尽量贴近 `server/db/schema.sql`，供 DAO 和 service 层使用。
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from server.core.enums import (
    Difficulty,
    ErrorCause,
    LearningState,
    ReviewStatus,
    TeachingStrategy,
    VisualAidType,
)


JsonObject = dict[str, Any]


class EntityModel(BaseModel):
    """数据库实体模型基类，统一枚举序列化方式。"""

    model_config = ConfigDict(use_enum_values=True)


class Student(EntityModel):
    """学生基础信息，对应 `student` 表。"""

    id: str = Field(..., description="学生唯一 ID，例如 stu_001。")
    name: str = Field(..., description="学生昵称或姓名，例如小宇。")
    grade: str = Field(..., description="学生年级，例如高一。")
    created_at: str = Field(..., description="学生记录创建时间，ISO 8601 字符串。")


class StudentProfile(EntityModel):
    """学生长期画像与记忆摘要，对应 `student_profile` 表。"""

    id: str = Field(..., description="画像唯一 ID。")
    student_id: str = Field(..., description="所属学生 ID，与 student.id 一对一关联。")
    weak_points: list[str] = Field(..., description="薄弱知识点 ID 列表。")
    recent_states: list[LearningState] = Field(..., description="近期学习状态序列，用于记忆加权。")
    effective_strategies: list[TeachingStrategy] = Field(..., description="对该学生历史有效的教学策略。")
    learning_summary: str | None = Field(default=None, description="长期学习画像自然语言摘要。")
    total_sessions: int = Field(..., description="累计完成的学习会话数。")
    updated_at: str = Field(..., description="画像最近更新时间，ISO 8601 字符串。")


class KnowledgePoint(EntityModel):
    """预置知识点字典，对应 `knowledge_point` 表。"""

    id: str = Field(..., description="知识点唯一 ID，例如 kp_003。")
    name: str = Field(..., description="知识点名称，例如二次函数最值。")
    subject: str = Field(..., description="所属学科，V0.1 固定为 math。")
    chapter: str | None = Field(default=None, description="所属章节名称。")
    parent_id: str | None = Field(default=None, description="上级知识点 ID；顶层知识点为空。")


class StudentKnowledge(EntityModel):
    """学生对单个知识点的掌握度记录，对应 `student_knowledge` 表。"""

    id: str = Field(..., description="掌握度记录唯一 ID。")
    student_id: str = Field(..., description="所属学生 ID。")
    knowledge_point_id: str = Field(..., description="关联知识点 ID。")
    mastery: int = Field(..., description="掌握度分数，范围 0-100。")
    attempts: int = Field(..., description="该知识点累计作答次数。")
    correct_count: int = Field(..., description="该知识点累计答对次数。")
    last_practiced_at: str | None = Field(default=None, description="最近练习该知识点的时间。")


class TypicalError(EntityModel):
    """题目典型错因条目，存放在 `question.typical_errors` JSON 字段中。"""

    cause: ErrorCause = Field(..., description="错因分类短码。")
    detail: str = Field(..., description="该错因在本题中的具体说明。")


class Question(EntityModel):
    """预置题库题目，对应 `question` 表。"""

    id: str = Field(..., description="题目唯一 ID，例如 q_001。")
    stem: str = Field(..., description="题干文本。")
    standard_answer: str = Field(..., description="标准答案文本。")
    solution: str = Field(..., description="标准解题步骤或关键思路。")
    difficulty: Difficulty = Field(..., description="题目难度。")
    typical_errors: list[TypicalError] = Field(..., description="本题典型错因列表。")
    visual_aid_type: VisualAidType = Field(..., description="建议使用的视觉辅助类型。")
    visual_aid_spec: JsonObject | None = Field(default=None, description="视觉辅助参数 JSON。")


class QuestionKnowledge(EntityModel):
    """题目与知识点的多对多关联记录，对应 `question_knowledge` 表。"""

    id: str = Field(..., description="题目-知识点关联记录唯一 ID。")
    question_id: str = Field(..., description="关联题目 ID。")
    knowledge_point_id: str = Field(..., description="关联知识点 ID。")


class LearningSession(EntityModel):
    """一次完整学习会话，对应 `session` 表。"""

    id: str = Field(..., description="学习会话唯一 ID。")
    student_id: str = Field(..., description="本次会话所属学生 ID。")
    started_at: str = Field(..., description="会话开始时间，ISO 8601 字符串。")
    ended_at: str | None = Field(default=None, description="会话结束时间；进行中为空。")
    dominant_state: LearningState | None = Field(default=None, description="本次会话的主导学习状态。")
    summary: str | None = Field(default=None, description="本次学习复盘摘要。")
    event_count: int = Field(default=0, description="本次会话累计学习事件数。")


class LearningEvent(EntityModel):
    """一轮“学生输入 -> 系统判断 -> 灵灵回应”的结构化事件，对应 `learning_event` 表。"""

    id: str = Field(..., description="学习事件唯一 ID。")
    session_id: str = Field(..., description="所属学习会话 ID。")
    student_id: str = Field(..., description="所属学生 ID，冗余保存便于查询。")
    question_id: str | None = Field(default=None, description="关联题目 ID；自由提问时为空。")
    sequence: int = Field(..., description="本会话内事件序号，从 1 开始。")
    student_input: str | None = Field(default=None, description="学生本轮输入原文。")
    student_answer: str | None = Field(default=None, description="学生本轮答案；非作答轮可为空。")
    is_correct: bool | None = Field(default=None, description="本轮是否答对；非作答轮为空。")
    knowledge_point_ids: list[str] = Field(..., description="本轮命中的知识点 ID 列表。")
    error_cause: ErrorCause | None = Field(default=None, description="本轮错因分类；答对或未归因时为空。")
    error_detail: str | None = Field(default=None, description="本轮错因的自然语言说明。")
    state: LearningState = Field(..., description="本轮识别出的学习状态。")
    state_evidence: str = Field(..., description="学习状态识别证据。")
    strategy: list[TeachingStrategy] = Field(..., description="本轮采用的教学策略组合。")
    strategy_reason: str = Field(..., description="选择这些策略的可解释原因。")
    care_triggered: bool = Field(..., description="本轮是否触发主动关怀。")
    visual_aid_used: VisualAidType = Field(..., description="本轮实际使用的视觉辅助类型。")
    tutor_response: str = Field(..., description="灵灵本轮最终回复文本。")
    created_at: str = Field(..., description="事件创建时间，ISO 8601 字符串。")


class ReviewTask(EntityModel):
    """会话结束后生成的主动复习任务，对应 `review_task` 表。"""

    id: str = Field(..., description="复习任务唯一 ID。")
    student_id: str = Field(..., description="任务所属学生 ID。")
    knowledge_point_id: str = Field(..., description="需要复习的知识点 ID。")
    source_event_id: str | None = Field(default=None, description="触发该任务的学习事件 ID。")
    reason: str = Field(..., description="生成该复习任务的原因。")
    recommended_question_id: str | None = Field(default=None, description="推荐复习题目 ID。")
    status: ReviewStatus = Field(..., description="复习任务当前状态。")
    due_date: str | None = Field(default=None, description="建议复习日期。")
    created_at: str = Field(..., description="任务创建时间，ISO 8601 字符串。")
