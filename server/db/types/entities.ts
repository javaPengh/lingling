import type {
  ErrorCause,
  LearningState,
  TeachingStrategy,
  VisualAidType
} from "../../../shared/api.js";

export type Difficulty = "easy" | "medium" | "hard";
export type ReviewStatus = "pending" | "done" | "skipped";
export type JsonRecord = Record<string, unknown>;

export interface Student {
  id: string;
  name: string;
  grade: string;
  createdAt: string;
}

export interface StudentProfile {
  id: string;
  studentId: string;
  weakPoints: string[];
  recentStates: LearningState[];
  effectiveStrategies: TeachingStrategy[];
  learningSummary: string | null;
  totalSessions: number;
  updatedAt: string;
}

export interface KnowledgePoint {
  id: string;
  name: string;
  subject: string;
  chapter: string | null;
  parentId: string | null;
}

export interface StudentKnowledge {
  id: string;
  studentId: string;
  knowledgePointId: string;
  mastery: number;
  attempts: number;
  correctCount: number;
  lastPracticedAt: string | null;
}

export interface TypicalError {
  cause: ErrorCause;
  detail: string;
}

export interface Question {
  id: string;
  stem: string;
  standardAnswer: string;
  solution: string;
  difficulty: Difficulty;
  typicalErrors: TypicalError[];
  visualAidType: VisualAidType;
  visualAidSpec: JsonRecord | null;
}

export interface QuestionKnowledge {
  id: string;
  questionId: string;
  knowledgePointId: string;
}

export interface LearningSession {
  id: string;
  studentId: string;
  startedAt: string;
  endedAt: string | null;
  dominantState: LearningState | null;
  summary: string | null;
  eventCount: number;
}

export interface LearningEvent {
  id: string;
  sessionId: string;
  studentId: string;
  questionId: string | null;
  sequence: number;
  studentInput: string | null;
  studentAnswer: string | null;
  isCorrect: boolean | null;
  knowledgePointIds: string[];
  errorCause: ErrorCause | null;
  errorDetail: string | null;
  state: LearningState;
  stateEvidence: string;
  strategy: TeachingStrategy[];
  strategyReason: string;
  careTriggered: boolean;
  visualAidUsed: VisualAidType;
  tutorResponse: string;
  createdAt: string;
}

export interface ReviewTask {
  id: string;
  studentId: string;
  knowledgePointId: string;
  sourceEventId: string | null;
  reason: string;
  recommendedQuestionId: string | null;
  status: ReviewStatus;
  dueDate: string | null;
  createdAt: string;
}
