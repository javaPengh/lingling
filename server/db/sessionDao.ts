import type {
  ErrorCause,
  LearningState,
  TeachingStrategy,
  VisualAidType
} from "../../shared/api.js";
import {
  boolToInt,
  dbOrDefault,
  intToBool,
  jsonText,
  parseJson,
  type Db
} from "./sqliteHelpers.js";
import type { LearningEvent, LearningSession } from "./types.js";

export function insertSession(session: LearningSession, db?: Db): void {
  dbOrDefault(db)
    .prepare(
      `INSERT INTO session (
        id, student_id, started_at, ended_at, dominant_state, summary, event_count
      ) VALUES (?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      session.id,
      session.studentId,
      session.startedAt,
      session.endedAt,
      session.dominantState,
      session.summary,
      session.eventCount
    );
}

export function getSessionById(id: string, db?: Db): LearningSession | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM session WHERE id = ?").get(id) as
    | {
        id: string;
        student_id: string;
        started_at: string;
        ended_at: string | null;
        dominant_state: LearningState | null;
        summary: string | null;
        event_count: number;
      }
    | undefined;

  return row
    ? {
        id: row.id,
        studentId: row.student_id,
        startedAt: row.started_at,
        endedAt: row.ended_at,
        dominantState: row.dominant_state,
        summary: row.summary,
        eventCount: row.event_count
      }
    : null;
}

export function insertLearningEvent(event: LearningEvent, db?: Db): void {
  dbOrDefault(db)
    .prepare(
      `INSERT INTO learning_event (
        id, session_id, student_id, question_id, sequence, student_input,
        student_answer, is_correct, knowledge_point_ids, error_cause, error_detail,
        state, state_evidence, strategy, strategy_reason, care_triggered,
        visual_aid_used, tutor_response, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      event.id,
      event.sessionId,
      event.studentId,
      event.questionId,
      event.sequence,
      event.studentInput,
      event.studentAnswer,
      boolToInt(event.isCorrect),
      jsonText(event.knowledgePointIds),
      event.errorCause,
      event.errorDetail,
      event.state,
      event.stateEvidence,
      jsonText(event.strategy),
      event.strategyReason,
      boolToInt(event.careTriggered),
      event.visualAidUsed,
      event.tutorResponse,
      event.createdAt
    );
}

export function getLearningEventById(id: string, db?: Db): LearningEvent | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM learning_event WHERE id = ?").get(id) as
    | {
        id: string;
        session_id: string;
        student_id: string;
        question_id: string | null;
        sequence: number;
        student_input: string | null;
        student_answer: string | null;
        is_correct: number | null;
        knowledge_point_ids: string | null;
        error_cause: ErrorCause | null;
        error_detail: string | null;
        state: LearningState;
        state_evidence: string;
        strategy: string;
        strategy_reason: string;
        care_triggered: number;
        visual_aid_used: VisualAidType;
        tutor_response: string;
        created_at: string;
      }
    | undefined;

  return row
    ? {
        id: row.id,
        sessionId: row.session_id,
        studentId: row.student_id,
        questionId: row.question_id,
        sequence: row.sequence,
        studentInput: row.student_input,
        studentAnswer: row.student_answer,
        isCorrect: intToBool(row.is_correct),
        knowledgePointIds: parseJson<string[]>(row.knowledge_point_ids, []),
        errorCause: row.error_cause,
        errorDetail: row.error_detail,
        state: row.state,
        stateEvidence: row.state_evidence,
        strategy: parseJson<TeachingStrategy[]>(row.strategy, []),
        strategyReason: row.strategy_reason,
        careTriggered: intToBool(row.care_triggered) ?? false,
        visualAidUsed: row.visual_aid_used,
        tutorResponse: row.tutor_response,
        createdAt: row.created_at
      }
    : null;
}
