// 通用枚举 ---------------------------------------------------------------

/** 学生当前学习/情绪状态，写入 learning_event.state。 */
export type LearningState = "stable" | "confused" | "frustrated" | "tired" | "anxious";

/** 教学编排器选择的教学策略，一轮回复可以组合多个策略。 */
export type TeachingStrategy =
  | "socratic"
  | "small_step"
  | "hint"
  | "care"
  | "humor"
  | "direct_explain";

/** 深图模块归因出的错因分类，用于观察面板和报告聚合。 */
export type ErrorCause =
  | "calculation"
  | "concept"
  | "misread"
  | "method"
  | "incomplete"
  | "careless"
  | "unknown";

/** 本轮实际使用的视觉辅助类型。 */
export type VisualAidType = "none" | "function_graph" | "geometry" | "annotation" | "diagram";

// 健康检查 ---------------------------------------------------------------

/** 后端健康检查响应。 */
export interface HealthResponse {
  /** 固定为 true，表示服务进程可响应。 */
  ok: true;

  /** 服务名，方便前端或脚本确认打到的是灵灵后端。 */
  service: "lingling-server";

  /** 当前大模型模式：mock 为离线假数据，live 为真实模型。 */
  mode: "mock" | "live";
}

// 学生列表 ---------------------------------------------------------------

/** 学生选择页使用的轻量学生信息，不包含完整长期记忆。 */
export interface StudentSummary {
  /** 学生 ID，对应数据库 student.id。 */
  id: string;

  /** 学生昵称/姓名，例如“小宇”。 */
  name: string;

  /** 年级，例如“高一”。 */
  grade: string;

  /** 前端卡片展示的人设标签；不是完整画像摘要。 */
  profileLabel?: string;
}

/** GET /api/students 的响应。 */
export interface StudentsListResponse {
  /** 可选择的预置学生列表。 */
  students: StudentSummary[];
}

// 学习会话与回合 ---------------------------------------------------------

/** 开始一次学习会话的请求。 */
export interface StartSessionRequest {
  /** 要进入学习的学生 ID。 */
  studentId: string;
}

/** 开始学习会话后的响应。 */
export interface StartSessionResponse {
  /** 新创建的会话 ID。 */
  sessionId: string;

  /** 本会话所属学生 ID。 */
  studentId: string;

  /** 会话开始时间，ISO 8601 字符串。 */
  startedAt: string;
}

/** 学生提交一轮输入给教学编排器的请求。 */
export interface LearningTurnRequest {
  /** 当前学习会话 ID。 */
  sessionId: string;

  /** 当前学生 ID。 */
  studentId: string;

  /** 本轮关联题目 ID；自由提问时可省略。 */
  questionId?: string;

  /** 学生本轮输入原文，可以是作答、追问或困惑表达。 */
  studentInput: string;

  /** 如果本轮是作答，这里放学生答案；非作答轮可省略。 */
  studentAnswer?: string;
}

/** 教学编排器处理一轮输入后的响应。 */
export interface LearningTurnResponse {
  /** 本轮写入 learning_event 后得到的事件 ID。 */
  eventId: string;

  /** 本轮识别出的学习状态。 */
  state: LearningState;

  /** 识别该状态的证据，会展示在观察面板。 */
  stateEvidence: string;

  /** 本轮采用的教学策略组合。 */
  strategy: TeachingStrategy[];

  /** 为什么选择这些策略，会展示在观察面板。 */
  strategyReason: string;

  /** 是否触发主动关怀。 */
  careTriggered: boolean;

  /** 本轮实际使用的视觉辅助。 */
  visualAidUsed: VisualAidType;

  /** 灵灵最终说给学生的话。 */
  tutorResponse: string;
}

// LLM 情绪识别 -----------------------------------------------------------

/** 规则层提供给大模型的客观信号。 */
export interface RuleSignal {
  /** 机器可读信号短码，例如 consecutive_wrong。 */
  code: string;

  /** 给大模型和观察面板看的自然语言说明。 */
  description: string;

  /** 信号强度；high 可触发更保守的 mock 判定或安全网逻辑。 */
  severity?: "low" | "medium" | "high";
}

/** recognizeEmotion 的输入，对应《灵灵人设与提示词规格》§3.2。 */
export interface EmotionRecognitionRequest {
  /** 学生本轮输入原文。 */
  studentInput: string;

  /** 本轮是否答对；非作答轮用 null 或省略。 */
  isCorrect?: boolean | null;

  /** 本轮命中的知识点 ID 列表。 */
  knowledgePointIds?: string[];

  /** 规则层先算出的客观信号列表。 */
  ruleSignals?: RuleSignal[];

  /** 忆感模块提供的历史记忆摘要。 */
  historySummary?: string;

  /** 最近 2-3 轮对话摘要，避免把长全文塞给模型。 */
  recentTurns?: string[];
}

/** recognizeEmotion 的输出，T1-2 验收要求字段齐全且为合法 JSON。 */
export interface EmotionRecognitionResponse {
  /** 五类学习状态之一。 */
  state: LearningState;

  /** 0-1 之间的置信度；V0.1 不入库，只给安全网参考。 */
  confidence: number;

  /** 状态判断依据，将写入 learning_event.state_evidence。 */
  evidence: string;
}

// LLM 教学回应 -----------------------------------------------------------

/** generateResponse 的输入，对应《灵灵人设与提示词规格》§5。 */
export interface GenerateResponseRequest {
  /** 情绪识别/编排器确定的当前学习状态。 */
  state: LearningState;

  /** 编排器选定的教学策略组合。 */
  strategy: TeachingStrategy[];

  /** 是否需要先接住情绪再回到题目。 */
  careTriggered: boolean;

  /** 本轮是否使用画图或其它视觉辅助。 */
  visualAidUsed: VisualAidType;

  /** 当前题目与标准解法；自由问答时可省略。 */
  question?: {
    /** 题干文本。 */
    stem: string;

    /** 标准解法或关键步骤，供兜底讲解使用。 */
    solution?: string;
  };

  /** 学生本轮输入原文。 */
  studentInput: string;

  /** 本轮是否答对；非作答轮用 null 或省略。 */
  isCorrect?: boolean | null;

  /** 深图模块识别出的错因分类。 */
  errorCause?: ErrorCause | null;

  /** 错因的自然语言说明。 */
  errorDetail?: string | null;
}

/** generateResponse 的输出。字段名沿用规格里的 tutor_response。 */
export interface GenerateResponseResponse {
  /** 灵灵最终对学生说的话；使用 snake_case 是为了和规格/验收字段保持一致。 */
  tutor_response: string;
}
