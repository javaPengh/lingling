import type { DatabaseSync } from "node:sqlite";
import type {
  ErrorCause,
  LearningState,
  StudentSummary,
  TeachingStrategy,
  VisualAidType
} from "../../shared/api.js";
import { getDatabase } from "./connection.js";

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

type Db = DatabaseSync;

function dbOrDefault(db?: Db): Db {
  return db ?? getDatabase();
}

function jsonText(value: unknown): string {
  return JSON.stringify(value);
}

function nullableJsonText(value: unknown | null): string | null {
  return value === null ? null : JSON.stringify(value);
}

function parseJson<T>(value: string | null, fallback: T): T {
  return value === null ? fallback : (JSON.parse(value) as T);
}

function boolToInt(value: boolean | null): number | null {
  if (value === null) {
    return null;
  }

  return value ? 1 : 0;
}

function intToBool(value: number | null): boolean | null {
  if (value === null) {
    return null;
  }

  return value === 1;
}

export function insertStudent(student: Student, db?: Db): void {
  dbOrDefault(db)
    .prepare("INSERT INTO student (id, name, grade, created_at) VALUES (?, ?, ?, ?)")
    .run(student.id, student.name, student.grade, student.createdAt);
}

export function getStudentById(id: string, db?: Db): Student | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM student WHERE id = ?").get(id) as
    | { id: string; name: string; grade: string; created_at: string }
    | undefined;

  return row
    ? {
        id: row.id,
        name: row.name,
        grade: row.grade,
        createdAt: row.created_at
      }
    : null;
}

export async function listStudents(): Promise<StudentSummary[]> {
  const rows = getDatabase()
    .prepare(
      `SELECT
        s.id,
        s.name,
        s.grade,
        p.learning_summary AS learningSummary
      FROM student s
      LEFT JOIN student_profile p ON p.student_id = s.id
      ORDER BY s.created_at ASC`
    )
    .all();

  return rows.map((row) => {
    const student = row as {
      id: string;
      name: string;
      grade: string;
      learningSummary: string | null;
    };

    return {
      id: student.id,
      name: student.name,
      grade: student.grade,
      profileLabel: student.learningSummary?.split(/[，。,.]/)[0]
    };
  });
}

export function insertStudentProfile(profile: StudentProfile, db?: Db): void {
  dbOrDefault(db)
    .prepare(
      `INSERT INTO student_profile (
        id, student_id, weak_points, recent_states, effective_strategies,
        learning_summary, total_sessions, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      profile.id,
      profile.studentId,
      jsonText(profile.weakPoints),
      jsonText(profile.recentStates),
      jsonText(profile.effectiveStrategies),
      profile.learningSummary,
      profile.totalSessions,
      profile.updatedAt
    );
}

export function getStudentProfileById(id: string, db?: Db): StudentProfile | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM student_profile WHERE id = ?").get(id) as
    | {
        id: string;
        student_id: string;
        weak_points: string | null;
        recent_states: string | null;
        effective_strategies: string | null;
        learning_summary: string | null;
        total_sessions: number;
        updated_at: string;
      }
    | undefined;

  return row
    ? {
        id: row.id,
        studentId: row.student_id,
        weakPoints: parseJson<string[]>(row.weak_points, []),
        recentStates: parseJson<LearningState[]>(row.recent_states, []),
        effectiveStrategies: parseJson<TeachingStrategy[]>(row.effective_strategies, []),
        learningSummary: row.learning_summary,
        totalSessions: row.total_sessions,
        updatedAt: row.updated_at
      }
    : null;
}

export function getStudentProfileByStudentId(studentId: string, db?: Db): StudentProfile | null {
  const row = dbOrDefault(db).prepare("SELECT id FROM student_profile WHERE student_id = ?").get(studentId) as
    | { id: string }
    | undefined;

  return row ? getStudentProfileById(row.id, db) : null;
}

export function insertKnowledgePoint(point: KnowledgePoint, db?: Db): void {
  dbOrDefault(db)
    .prepare("INSERT INTO knowledge_point (id, name, subject, chapter, parent_id) VALUES (?, ?, ?, ?, ?)")
    .run(point.id, point.name, point.subject, point.chapter, point.parentId);
}

export function getKnowledgePointById(id: string, db?: Db): KnowledgePoint | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM knowledge_point WHERE id = ?").get(id) as
    | { id: string; name: string; subject: string; chapter: string | null; parent_id: string | null }
    | undefined;

  return row
    ? {
        id: row.id,
        name: row.name,
        subject: row.subject,
        chapter: row.chapter,
        parentId: row.parent_id
      }
    : null;
}

export function insertStudentKnowledge(record: StudentKnowledge, db?: Db): void {
  dbOrDefault(db)
    .prepare(
      `INSERT INTO student_knowledge (
        id, student_id, knowledge_point_id, mastery, attempts, correct_count, last_practiced_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      record.id,
      record.studentId,
      record.knowledgePointId,
      record.mastery,
      record.attempts,
      record.correctCount,
      record.lastPracticedAt
    );
}

export function getStudentKnowledgeById(id: string, db?: Db): StudentKnowledge | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM student_knowledge WHERE id = ?").get(id) as
    | {
        id: string;
        student_id: string;
        knowledge_point_id: string;
        mastery: number;
        attempts: number;
        correct_count: number;
        last_practiced_at: string | null;
      }
    | undefined;

  return row
    ? {
        id: row.id,
        studentId: row.student_id,
        knowledgePointId: row.knowledge_point_id,
        mastery: row.mastery,
        attempts: row.attempts,
        correctCount: row.correct_count,
        lastPracticedAt: row.last_practiced_at
      }
    : null;
}

export function insertQuestion(question: Question, db?: Db): void {
  dbOrDefault(db)
    .prepare(
      `INSERT INTO question (
        id, stem, standard_answer, solution, difficulty,
        typical_errors, visual_aid_type, visual_aid_spec
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      question.id,
      question.stem,
      question.standardAnswer,
      question.solution,
      question.difficulty,
      jsonText(question.typicalErrors),
      question.visualAidType,
      nullableJsonText(question.visualAidSpec)
    );
}

export function getQuestionById(id: string, db?: Db): Question | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM question WHERE id = ?").get(id) as
    | {
        id: string;
        stem: string;
        standard_answer: string;
        solution: string;
        difficulty: Difficulty;
        typical_errors: string | null;
        visual_aid_type: VisualAidType;
        visual_aid_spec: string | null;
      }
    | undefined;

  return row
    ? {
        id: row.id,
        stem: row.stem,
        standardAnswer: row.standard_answer,
        solution: row.solution,
        difficulty: row.difficulty,
        typicalErrors: parseJson<TypicalError[]>(row.typical_errors, []),
        visualAidType: row.visual_aid_type,
        visualAidSpec: parseJson<JsonRecord | null>(row.visual_aid_spec, null)
      }
    : null;
}

export function insertQuestionKnowledge(record: QuestionKnowledge, db?: Db): void {
  dbOrDefault(db)
    .prepare("INSERT INTO question_knowledge (id, question_id, knowledge_point_id) VALUES (?, ?, ?)")
    .run(record.id, record.questionId, record.knowledgePointId);
}

export function getQuestionKnowledgeById(id: string, db?: Db): QuestionKnowledge | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM question_knowledge WHERE id = ?").get(id) as
    | { id: string; question_id: string; knowledge_point_id: string }
    | undefined;

  return row
    ? {
        id: row.id,
        questionId: row.question_id,
        knowledgePointId: row.knowledge_point_id
      }
    : null;
}

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

export function insertReviewTask(task: ReviewTask, db?: Db): void {
  dbOrDefault(db)
    .prepare(
      `INSERT INTO review_task (
        id, student_id, knowledge_point_id, source_event_id, reason,
        recommended_question_id, status, due_date, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    )
    .run(
      task.id,
      task.studentId,
      task.knowledgePointId,
      task.sourceEventId,
      task.reason,
      task.recommendedQuestionId,
      task.status,
      task.dueDate,
      task.createdAt
    );
}

export function getReviewTaskById(id: string, db?: Db): ReviewTask | null {
  const row = dbOrDefault(db).prepare("SELECT * FROM review_task WHERE id = ?").get(id) as
    | {
        id: string;
        student_id: string;
        knowledge_point_id: string;
        source_event_id: string | null;
        reason: string;
        recommended_question_id: string | null;
        status: ReviewStatus;
        due_date: string | null;
        created_at: string;
      }
    | undefined;

  return row
    ? {
        id: row.id,
        studentId: row.student_id,
        knowledgePointId: row.knowledge_point_id,
        sourceEventId: row.source_event_id,
        reason: row.reason,
        recommendedQuestionId: row.recommended_question_id,
        status: row.status,
        dueDate: row.due_date,
        createdAt: row.created_at
      }
    : null;
}
