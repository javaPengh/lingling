"""学习状态识别服务。

规则层负责提取客观信号和安全网，LLM 负责语义裁决；LLM 不可用时使用规则兜底。
"""

from dataclasses import dataclass
import sqlite3

from server.core.enums import LearningState
from server.llm.base import LlmError
from server.llm.client import get_llm_client
from server.models.entities import LearningEvent
from server.models.schemas import EmotionRecognitionInput, RuleSignal
from server.services.memory import MemorySnapshot


@dataclass(frozen=True)
class StateRecognitionResult:
    """状态识别结果，包含最终状态、证据、规则信号和受阻次数。"""

    state: LearningState
    evidence: str
    rule_signals: list[RuleSignal]
    obstruction_count: int


def recognize_state(
    connection: sqlite3.Connection,
    student_input: str,
    is_correct: bool | None,
    knowledge_point_ids: list[str],
    prior_events: list[LearningEvent],
    memory: MemorySnapshot,
) -> StateRecognitionResult:
    """识别本轮学习状态，并应用规则安全网。"""

    del connection
    rule_signals = collect_rule_signals(student_input, is_correct, knowledge_point_ids, prior_events, memory)
    obstruction_count = _obstruction_count(knowledge_point_ids, prior_events, is_correct, student_input)
    payload = EmotionRecognitionInput(
        student_input=student_input,
        is_correct=is_correct,
        knowledge_point_ids=knowledge_point_ids,
        rule_signals=rule_signals,
        history_summary=memory.history_summary,
        recent_turns=[event.student_input or "" for event in prior_events[-3:]],
    )
    baseline_state, baseline_evidence = _baseline_state(rule_signals, is_correct)
    try:
        llm_result = get_llm_client().recognize_emotion(payload)
        state = LearningState(llm_result.state)
        evidence = llm_result.evidence
    except (LlmError, ValueError):
        state = baseline_state
        evidence = f"LLM不可用，采用规则兜底：{baseline_evidence}"

    safe_state, safety_note = _apply_safety_net(state, rule_signals, baseline_state)
    if safety_note:
        evidence = f"{evidence}；{safety_note}"
    if _has_negative_memory(memory) and safe_state == LearningState.CONFUSED:
        evidence = f"{evidence}；读取到近期负面状态，提前提高关怀敏感度"
    return StateRecognitionResult(safe_state, evidence, rule_signals, obstruction_count)


def collect_rule_signals(
    student_input: str,
    is_correct: bool | None,
    knowledge_point_ids: list[str],
    prior_events: list[LearningEvent],
    memory: MemorySnapshot,
) -> list[RuleSignal]:
    """从学生文本、作答结果、历史事件和长期记忆中提取规则信号。"""

    text = student_input.lower()
    signals: list[RuleSignal] = []
    if any(word in text for word in ["算了", "放弃", "不会", "搞不定"]):
        signals.append(RuleSignal(code="sig_giveup", description="学生出现放弃倾向", severity="high"))
    if any(word in text for word in ["太笨", "我笨", "肯定不行"]):
        signals.append(RuleSignal(code="sig_self_doubt", description="学生出现自我否定表达", severity="high"))
    if any(word in text for word in ["考试", "来不及", "万一", "肯定考"]):
        signals.append(RuleSignal(code="sig_anxiety", description="学生表达考试或时间焦虑", severity="high"))
    if any(word in text for word in ["累", "困", "不想学", "学不动"]):
        signals.append(RuleSignal(code="sig_tired", description="学生表达疲惫或注意力下降", severity="medium"))
    if any(word in text for word in ["没懂", "不懂", "啊？", "为什么", "卡住", "关系"]):
        signals.append(RuleSignal(code="sig_confusion", description="学生明确表达困惑", severity="medium"))
    if is_correct is False:
        signals.append(RuleSignal(code="sig_wrong_answer", description="本轮作答错误", severity="medium"))
    obstruction_count = _obstruction_count(knowledge_point_ids, prior_events, is_correct, student_input)
    if obstruction_count >= 3:
        signals.append(RuleSignal(code="sig_consecutive_wrong", description="同一知识点连续受阻达到2次以上", severity="high"))
    elif obstruction_count >= 2:
        signals.append(RuleSignal(code="sig_repeated_obstruction", description="同一知识点第2次受阻，优先触发画图或提示", severity="medium"))
    if _has_negative_memory(memory):
        signals.append(RuleSignal(code="mem_recent_negative", description="长期记忆显示近期负面状态偏多", severity="medium"))
    return signals


def _baseline_state(signals: list[RuleSignal], is_correct: bool | None) -> tuple[LearningState, str]:
    codes = {signal.code for signal in signals}
    if {"sig_giveup", "sig_self_doubt"} & codes:
        return LearningState.FRUSTRATED, "命中放弃/自我否定强信号"
    if "sig_anxiety" in codes:
        return LearningState.ANXIOUS, "命中焦虑表达"
    if "sig_consecutive_wrong" in codes:
        return LearningState.FRUSTRATED, "连续受阻导致状态滑坡"
    if "sig_tired" in codes:
        return LearningState.TIRED, "命中疲惫表达"
    if "sig_confusion" in codes or is_correct is False:
        return LearningState.CONFUSED, "表达困惑或本轮作答错误"
    return LearningState.STABLE, "无负面信号且能继续推进"


def _apply_safety_net(
    llm_state: LearningState, signals: list[RuleSignal], baseline_state: LearningState
) -> tuple[LearningState, str | None]:
    codes = {signal.code for signal in signals}
    if {"sig_giveup", "sig_self_doubt"} & codes and llm_state not in {LearningState.FRUSTRATED, LearningState.ANXIOUS}:
        return LearningState.FRUSTRATED, f"大模型判 {llm_state}，但命中自我否定/放弃强信号，安全网修正为 frustrated"
    if "sig_anxiety" in codes and llm_state == LearningState.STABLE:
        return LearningState.ANXIOUS, "大模型判 stable，但命中焦虑强信号，安全网修正为 anxious"
    if "sig_consecutive_wrong" in codes and llm_state == LearningState.STABLE:
        return LearningState.FRUSTRATED, "大模型判 stable，但连续受阻，安全网修正为 frustrated"
    return llm_state or baseline_state, None


def _obstruction_count(
    knowledge_point_ids: list[str],
    prior_events: list[LearningEvent],
    is_correct: bool | None,
    student_input: str,
) -> int:
    if is_correct is True:
        return 0
    if not knowledge_point_ids:
        return 0
    target = set(knowledge_point_ids)
    count = 1 if (is_correct is False or any(word in student_input for word in ["没懂", "不会", "卡住"])) else 0
    for event in reversed(prior_events):
        if not target.intersection(event.knowledge_point_ids):
            continue
        if event.is_correct is False or event.state in {LearningState.CONFUSED, LearningState.FRUSTRATED, "confused", "frustrated"}:
            count += 1
        else:
            break
    return count


def _has_negative_memory(memory: MemorySnapshot) -> bool:
    if not memory.profile:
        return False
    negative = [state for state in memory.profile.recent_states if state in {"confused", "frustrated", "anxious", "tired"}]
    return len(negative) >= 2
