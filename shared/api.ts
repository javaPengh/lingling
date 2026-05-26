export type LearningState = "stable" | "confused" | "frustrated" | "tired" | "anxious";

export type TeachingStrategy =
  | "socratic"
  | "small_step"
  | "hint"
  | "care"
  | "humor"
  | "direct_explain";

export type ErrorCause =
  | "calculation"
  | "concept"
  | "misread"
  | "method"
  | "incomplete"
  | "careless"
  | "unknown";

export type VisualAidType = "none" | "function_graph" | "geometry" | "annotation" | "diagram";

export interface HealthResponse {
  ok: true;
  service: "lingling-server";
  mode: "mock" | "live";
}

export interface StudentSummary {
  id: string;
  name: string;
  grade: string;
  profileLabel?: string;
}

export interface StudentsListResponse {
  students: StudentSummary[];
}

export interface StartSessionRequest {
  studentId: string;
}

export interface StartSessionResponse {
  sessionId: string;
  studentId: string;
  startedAt: string;
}

export interface LearningTurnRequest {
  sessionId: string;
  studentId: string;
  questionId?: string;
  studentInput: string;
  studentAnswer?: string;
}

export interface LearningTurnResponse {
  eventId: string;
  state: LearningState;
  stateEvidence: string;
  strategy: TeachingStrategy[];
  strategyReason: string;
  careTriggered: boolean;
  visualAidUsed: VisualAidType;
  tutorResponse: string;
}
