import type { LearningState, StudentSummary, TeachingStrategy } from "../../shared/api.js";
import { dbOrDefault, jsonText, parseJson, type Db } from "./sqliteHelpers.js";
import type { Student, StudentKnowledge, StudentProfile } from "./types.js";

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

export function listStudents(db?: Db): StudentSummary[] {
  const rows = dbOrDefault(db)
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
