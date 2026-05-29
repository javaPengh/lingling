import type {
  GenerateResponseRequest,
  GenerateResponseResponse
} from "../../../shared/api.js";

export function generateResponseMock(
  input: GenerateResponseRequest
): GenerateResponseResponse {
  if (input.careTriggered || input.strategy.includes("care")) {
    return {
      tutor_response:
        "先别急，这一步卡住很正常。我们把题目拆小一点：先看你现在最确定的条件是哪一个？"
    };
  }

  if (input.strategy.includes("small_step")) {
    return {
      tutor_response: "我们只往前走一步：先把题目里的关键条件圈出来，再判断它能推出什么。"
    };
  }

  if (input.strategy.includes("hint")) {
    return {
      tutor_response: "给你一个小提示：先别急着算结果，看看这个条件对应的是哪个知识点。"
    };
  }

  if (input.strategy.includes("direct_explain")) {
    return {
      tutor_response: "这题的关键是先确定方法，再代入计算。我先把第一步讲清楚：从已知条件建立关系式。"
    };
  }

  return {
    tutor_response: "我们先从你已经确定的一步开始。你觉得题目里最有用的信息是哪一句？"
  };
}
