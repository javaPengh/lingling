"""API 与 LLM 调用的数据契约。

本文件描述 HTTP 请求/响应和 LLM 适配层输入输出，不直接等同数据库表。
字段在 Python 内部使用 snake_case，对外通过 `ApiModel` 自动暴露为 camelCase。
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from server.core.enums import AccountRole, LearningState, TeachingStrategy, VisualAidType
from server.models.entities import LearningEvent, ReviewTask, StudentKnowledge, StudentProfile


def to_camel(value: str) -> str:
    """将 snake_case 字段名转换为前端使用的 camelCase。"""

    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class ApiModel(BaseModel):
    """API DTO 基类，统一 camelCase 别名和枚举序列化。"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,
    )


class HealthResponse(ApiModel):
    """健康检查响应，供前端确认后端服务与 LLM 模式。"""

    ok: bool = Field(default=True, description="服务是否可响应，健康检查固定为 true。")
    service: str = Field(default="lingling-server", description="服务名称，供前端确认命中的后端。")
    mode: str = Field(..., description="当前 LLM 模式，取值为 mock 或 live。")


class StudentSummary(ApiModel):
    """学生选择页使用的轻量学生卡片数据。"""

    id: str = Field(..., description="学生唯一 ID。")
    name: str = Field(..., description="学生昵称或姓名。")
    grade: str = Field(..., description="学生年级。")
    profile_label: str | None = Field(default=None, description="学生卡片上展示的短画像标签。")


class StudentsListResponse(ApiModel):
    """学生列表接口响应。"""

    students: list[StudentSummary] = Field(..., description="可选择的预置学生列表。")


class AccountSummary(ApiModel):
    """登录入口使用的预置账号摘要。"""

    id: str = Field(..., description="账号唯一 ID。")
    username: str = Field(..., description="登录账号名。")
    role: AccountRole = Field(..., description="账号角色：student、parent 或 teacher。")
    display_name: str = Field(..., description="登录入口展示名称。")
    student_id: str | None = Field(default=None, description="学生账号对应的本人学生 ID；家长和老师账号为空。")


class AccountsListResponse(ApiModel):
    """账号列表接口响应。"""

    accounts: list[AccountSummary] = Field(..., description="登录入口可选择的预置账号列表。")


class AccountStudentsResponse(ApiModel):
    """某个账号可查看或可进入的学生范围。"""

    account: AccountSummary = Field(..., description="当前查询的账号摘要。")
    students: list[StudentSummary] = Field(..., description="该账号可查看或可进入的学生列表。")


class LoginRequest(ApiModel):
    """登录页提交的账号密码请求。"""

    account: str = Field(..., description="用户输入的登录账号；后端兼容 username、账号 ID 或展示名。")
    password: str = Field(..., description="用户输入的明文密码，只用于本次校验，不入库。")


class LoginResponse(ApiModel):
    """账号密码校验成功后的角色分流结果。"""

    account: AccountSummary = Field(..., description="登录成功的账号摘要。")
    students: list[StudentSummary] = Field(..., description="该账号可进入或可查看的学生范围。")
    landing_page: str = Field(..., description="前端登录成功后的目标页面：student_learning、parent_report 或 teacher_report。")


class StartSessionRequest(ApiModel):
    """开始学习会话的请求体。"""

    student_id: str = Field(..., description="要开始学习的学生 ID。")


class StartSessionResponse(ApiModel):
    """开始学习会话后的响应，包含会话信息和开场上下文。"""

    session_id: str = Field(..., description="新创建的学习会话 ID。")
    student_id: str = Field(..., description="本次会话所属学生 ID。")
    started_at: str = Field(..., description="会话开始时间，ISO 8601 字符串。")
    opening_message: str = Field(..., description="根据学生画像生成的灵灵开场语。")
    memory_summary: str = Field(..., description="会话开始时读取到的长期记忆摘要。")
    recommended_question_id: str | None = Field(default=None, description="推荐进入学习的题目 ID。")


class LearningTurnRequest(ApiModel):
    """学生提交一轮输入给教学编排器的请求体。"""

    session_id: str = Field(..., description="当前学习会话 ID。")
    student_id: str = Field(..., description="当前学生 ID。")
    question_id: str | None = Field(default=None, description="本轮关联题目 ID；自由提问时为空。")
    student_input: str = Field(..., description="学生本轮输入原文。")
    student_answer: str | None = Field(default=None, description="学生本轮答案；非作答轮可为空。")


class LearningTurnResponse(ApiModel):
    """教学编排器处理一轮输入后的响应。"""

    event_id: str = Field(..., description="本轮写入数据库后的学习事件 ID。")
    state: LearningState = Field(..., description="本轮识别出的学习状态。")
    state_evidence: str = Field(..., description="识别该学习状态的证据。")
    strategy: list[TeachingStrategy] = Field(..., description="本轮采用的教学策略组合。")
    strategy_reason: str = Field(..., description="选择这些策略的可解释原因。")
    care_triggered: bool = Field(..., description="本轮是否触发主动关怀。")
    visual_aid_used: VisualAidType = Field(..., description="本轮实际使用的视觉辅助类型。")
    tutor_response: str = Field(..., description="灵灵最终说给学生的话。")
    is_correct: bool | None = Field(default=None, description="本轮是否答对；非作答轮为空。")
    error_cause: str | None = Field(default=None, description="本轮错因分类；答对或未归因时为空。")
    error_detail: str | None = Field(default=None, description="本轮错因自然语言说明。")
    knowledge_point_ids: list[str] = Field(default_factory=list, description="本轮命中的知识点 ID 列表。")


class FinishSessionResponse(ApiModel):
    """结束会话后的写回结果与复盘响应。"""

    session_id: str = Field(..., description="已结束的学习会话 ID。")
    student_id: str = Field(..., description="本次会话所属学生 ID。")
    summary: str = Field(..., description="本次学习复盘摘要。")
    dominant_state: LearningState | None = Field(default=None, description="本次会话主导学习状态。")
    event_count: int = Field(..., description="本次会话累计学习事件数。")
    review_tasks: list[ReviewTask] = Field(..., description="本次会话生成的复习任务列表。")
    updated_profile: StudentProfile | None = Field(default=None, description="写回后的学生画像。")


class ObserverEvent(ApiModel):
    """观察面板中的单轮事件包装，预留展示规则信号。"""

    event: LearningEvent = Field(..., description="本轮结构化学习事件。")
    signals: list[str] = Field(..., description="本轮命中的规则信号说明。")


class ObserverSessionResponse(ApiModel):
    """观察面板按会话查询到的决策链路数据。"""

    session_id: str = Field(..., description="观察的学习会话 ID。")
    student_id: str = Field(..., description="本次会话所属学生 ID。")
    memory_summary: str = Field(..., description="会话相关的长期记忆摘要。")
    events: list[LearningEvent] = Field(..., description="该会话下的学习事件列表。")
    review_tasks: list[ReviewTask] = Field(..., description="该会话产生的复习任务列表。")


class ReportResponse(ApiModel):
    """报告预览接口响应，聚合教师/家长视角摘要。"""

    student_id: str = Field(..., description="报告所属学生 ID。")
    student_name: str = Field(..., description="报告所属学生姓名。")
    teacher_summary: str = Field(..., description="面向教师的学习摘要。")
    parent_summary: str = Field(..., description="面向家长的学习摘要。")
    weak_points: list[StudentKnowledge] = Field(..., description="当前薄弱知识点掌握记录。")
    review_tasks: list[ReviewTask] = Field(..., description="该学生的复习任务列表。")
    recent_events: list[LearningEvent] = Field(..., description="该学生近期学习事件列表。")
    profile: StudentProfile | None = Field(default=None, description="学生长期画像。")


class RuleSignal(ApiModel):
    """规则层提供给 LLM 的客观信号。"""

    code: str = Field(..., description="规则信号短码。")
    description: str = Field(..., description="规则信号的自然语言说明。")
    severity: str = Field(default="low", description="信号强度，取值为 low、medium 或 high。")


class EmotionRecognitionInput(ApiModel):
    """情绪识别 LLM 调用输入。"""

    student_input: str = Field(..., description="学生本轮输入原文。")
    is_correct: bool | None = Field(default=None, description="本轮是否答对；非作答轮为空。")
    knowledge_point_ids: list[str] = Field(default_factory=list, description="本轮命中的知识点 ID 列表。")
    rule_signals: list[RuleSignal] = Field(default_factory=list, description="规则层提取的客观信号列表。")
    history_summary: str | None = Field(default=None, description="忆感模块提供的历史记忆摘要。")
    recent_turns: list[str] = Field(default_factory=list, description="最近 2-3 轮学生输入摘要。")


class EmotionRecognitionResult(ApiModel):
    """情绪识别 LLM 调用输出。"""

    state: LearningState = Field(..., description="LLM 识别出的学习状态。")
    confidence: float = Field(..., description="LLM 对状态判断的置信度，范围 0-1。")
    evidence: str = Field(..., description="LLM 给出的状态判断依据。")


class GenerateResponseInput(ApiModel):
    """教学回应生成 LLM 调用输入。"""

    state: LearningState = Field(..., description="编排器确定的当前学习状态。")
    strategy: list[TeachingStrategy] = Field(..., description="编排器选择的教学策略组合。")
    care_triggered: bool = Field(..., description="是否需要先主动关怀再回到题目。")
    visual_aid_used: VisualAidType = Field(..., description="本轮是否使用视觉辅助及其类型。")
    question: dict[str, Any] | None = Field(default=None, description="当前题目上下文，通常包含 stem 和 solution。")
    student_input: str = Field(..., description="学生本轮输入原文。")
    is_correct: bool | None = Field(default=None, description="本轮是否答对；非作答轮为空。")
    error_cause: str | None = Field(default=None, description="深图模块识别出的错因分类。")
    error_detail: str | None = Field(default=None, description="错因自然语言说明。")


class GenerateResponseResult(ApiModel):
    """教学回应生成 LLM 调用输出。"""

    tutor_response: str = Field(..., description="灵灵最终对学生说的话。")
