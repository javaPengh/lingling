"""离线 mock LLM 客户端。

用于本地开发、断网演示和 live 模型异常时的兜底。
"""

from server.core.enums import LearningState, TeachingStrategy, VisualAidType
from server.llm.base import LlmClient
from server.models.schemas import (
    EmotionRecognitionInput,
    EmotionRecognitionResult,
    GenerateResponseInput,
    GenerateResponseResult,
)


class MockLlmClient(LlmClient):
    """基于规则信号生成稳定可复现结果的 mock 实现。"""

    def recognize_emotion(self, payload: EmotionRecognitionInput) -> EmotionRecognitionResult:
        """根据规则信号和学生文本模拟情绪识别。"""

        codes = {signal.code for signal in payload.rule_signals}
        text = payload.student_input
        state = LearningState.STABLE
        confidence = 0.72
        evidence = "未命中明显负面表达，学习状态平稳"

        if {"sig_giveup", "sig_self_doubt"} & codes:
            state = LearningState.FRUSTRATED
            confidence = 0.94
            evidence = "学生出现放弃或自我否定表达，规则信号指向挫败"
        elif "sig_anxiety" in codes:
            state = LearningState.ANXIOUS
            confidence = 0.9
            evidence = "学生提到考试担忧、来不及等焦虑表达"
        elif "sig_tired" in codes:
            state = LearningState.TIRED
            confidence = 0.86
            evidence = "学生表达疲惫或注意力下降"
        elif "sig_consecutive_wrong" in codes:
            state = LearningState.FRUSTRATED
            confidence = 0.88
            evidence = "同一会话连续受阻，规则层提示学习状态滑坡"
        elif "sig_confusion" in codes or payload.is_correct is False:
            state = LearningState.CONFUSED
            confidence = 0.82
            evidence = "学生表达没懂或本轮作答错误，当前更像困惑"
        elif payload.is_correct is True:
            state = LearningState.STABLE
            confidence = 0.86
            evidence = "本轮能跟上关键步骤并答对，状态回稳"

        if "哦我可太会了" in text:
            state = LearningState.FRUSTRATED
            confidence = 0.89
            evidence = "学生使用反讽表达，按语义识别为受挫而非平稳"

        return EmotionRecognitionResult(state=state, confidence=confidence, evidence=evidence)

    def generate_response(self, payload: GenerateResponseInput) -> GenerateResponseResult:
        """根据状态和策略生成离线教学回应。"""

        strategies = set(payload.strategy)
        question = payload.question or {}
        solution = question.get("solution") or ""

        if TeachingStrategy.CARE in strategies and payload.state == LearningState.FRUSTRATED:
            text = "先别急，这不是笨，是含参题本来就爱拐弯。我们把它切成一小块：先只看 a<0 时，对称轴在区间哪边？"
        elif payload.state == LearningState.ANXIOUS:
            text = "先稳一下，考试感会把题目放大。我们只处理当前一步：你先告诉我这题最该建立哪两个向量？"
        elif payload.state == LearningState.TIRED:
            text = "看起来有点累了，我们把这一轮缩短：只做一个最小判断，做完就停一下也可以。"
        elif payload.is_correct is True:
            text = "对，就是这个方向。你已经抓住关键点了，我们再往前追问一步：这个结论对应的是哪一种参数范围？"
        elif TeachingStrategy.HINT in strategies:
            text = "你现在卡在关键关系上。提示一下：二次函数在区间上的最值，先看对称轴和区间的位置关系。"
        elif TeachingStrategy.DIRECT_EXPLAIN in strategies and solution:
            text = f"这一步我直接帮你收一下：{solution}"
        else:
            text = "我们先不急着算答案。你说说看，这道题里最值得先确定的量是什么？"

        if payload.visual_aid_used != VisualAidType.NONE and "画" not in text:
            text += " 我会同时把图形辅助打开，帮你盯住关键位置。"

        return GenerateResponseResult(tutor_response=text)
