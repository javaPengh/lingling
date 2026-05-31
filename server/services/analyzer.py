"""深图/判题服务。

V0.1 用规则实现题目匹配、知识点命中和错因归因，后续可替换为更强的分析能力。
"""

from dataclasses import dataclass
import re
import sqlite3

from server.dao.question_dao import get_question, list_question_knowledge_ids
from server.models.entities import Question


@dataclass(frozen=True)
class AnalysisResult:
    """一轮输入的题目分析结果。"""

    question: Question | None
    knowledge_point_ids: list[str]
    is_correct: bool | None
    error_cause: str | None
    error_detail: str | None


def analyze_turn(
    connection: sqlite3.Connection,
    question_id: str | None,
    student_input: str,
    student_answer: str | None,
) -> AnalysisResult:
    """分析学生本轮输入，返回是否答对、命中知识点和错因。"""

    if not question_id:
        return AnalysisResult(None, [], None, None, None)

    question = get_question(connection, question_id)
    if question is None:
        raise ValueError(f"Question not found: {question_id}")

    knowledge_point_ids = list_question_knowledge_ids(connection, question_id)
    answer_text = (student_answer or "").strip()
    if not answer_text and not _looks_like_answer(student_input):
        return AnalysisResult(question, knowledge_point_ids, None, None, None)

    answer_text = answer_text or student_input
    is_correct = _judge_answer(question, answer_text)
    if is_correct:
        return AnalysisResult(question, knowledge_point_ids, True, None, None)

    typical_error = question.typical_errors[0] if question.typical_errors else None
    return AnalysisResult(
        question,
        knowledge_point_ids,
        False,
        typical_error.cause if typical_error else "unknown",
        typical_error.detail if typical_error else "未命中标准答案，需进一步追问确认错因",
    )


def _looks_like_answer(text: str) -> bool:
    markers = ["=", "<", "≤", ">", "≥", "概率", "最小值", "f(", "√", "/"]
    return any(marker in text for marker in markers)


def _normalize(text: str) -> str:
    text = text.lower().replace(" ", "")
    return re.sub(r"[。；;，,（）()【】\[\]{}]", "", text)


def _judge_answer(question: Question, answer: str) -> bool:
    normalized = _normalize(answer)
    if question.id == "q_001":
        full_cases = all(token in normalized for token in ["a<0", "0≤a≤2", "a>2"])
        partial_step = "f0=1" in normalized or "f(0)=1" in normalized or "f（0）=1" in normalized
        return full_cases or partial_step
    if question.id == "q_002":
        return "1" in normalized and ("x=2" in normalized or "最小值" in normalized)
    if question.id == "q_003":
        return "m<1" in normalized
    if question.id == "q_004":
        return "2≤x≤3" in normalized or "2<=x<=3" in normalized
    if question.id == "q_005":
        return "a≤1" in normalized or "a<=1" in normalized
    if question.id == "q_006":
        return "√3/3" in normalized or "根号3/3" in normalized
    if question.id == "q_007":
        return "2/5" in normalized
    return _normalize(question.standard_answer) in normalized
