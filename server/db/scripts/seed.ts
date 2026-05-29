import { pathToFileURL } from "node:url";
import type { DatabaseSync } from "node:sqlite";
import { getDatabase } from "../connection.js";
import {
  seedKnowledgePoints,
  seedQuestionKnowledge,
  seedQuestions,
  seedStudentKnowledge,
  seedStudentProfiles,
  seedStudents
} from "../seeds/t1SeedData.js";

export interface SeedSummary {
  students: number;
  studentProfiles: number;
  knowledgePoints: number;
  studentKnowledge: number;
  questions: number;
  questionKnowledge: number;
}

export function seedDatabase(db = getDatabase()): SeedSummary {
  db.exec("BEGIN");

  try {
    seedStudents.forEach((student) => upsertStudent(db, student));
    seedKnowledgePoints.forEach((point) => upsertKnowledgePoint(db, point));
    seedStudentProfiles.forEach((profile) => upsertStudentProfile(db, profile));
    seedStudentKnowledge.forEach((record) => upsertStudentKnowledge(db, record));
    seedQuestions.forEach((question) => upsertQuestion(db, question));
    seedQuestionKnowledge.forEach((record) => upsertQuestionKnowledge(db, record));

    db.exec("COMMIT");
  } catch (error) {
    db.exec("ROLLBACK");
    throw error;
  }

  return {
    students: seedStudents.length,
    studentProfiles: seedStudentProfiles.length,
    knowledgePoints: seedKnowledgePoints.length,
    studentKnowledge: seedStudentKnowledge.length,
    questions: seedQuestions.length,
    questionKnowledge: seedQuestionKnowledge.length
  };
}

function upsertStudent(db: DatabaseSync, student: (typeof seedStudents)[number]): void {
  db.prepare(
    `INSERT INTO student (id, name, grade, created_at)
     VALUES (?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       name = excluded.name,
       grade = excluded.grade,
       created_at = excluded.created_at`
  ).run(student.id, student.name, student.grade, student.createdAt);
}

function upsertStudentProfile(
  db: DatabaseSync,
  profile: (typeof seedStudentProfiles)[number]
): void {
  db.prepare(
    `INSERT INTO student_profile (
       id, student_id, weak_points, recent_states, effective_strategies,
       learning_summary, total_sessions, updated_at
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       student_id = excluded.student_id,
       weak_points = excluded.weak_points,
       recent_states = excluded.recent_states,
       effective_strategies = excluded.effective_strategies,
       learning_summary = excluded.learning_summary,
       total_sessions = excluded.total_sessions,
       updated_at = excluded.updated_at`
  ).run(
    profile.id,
    profile.studentId,
    JSON.stringify(profile.weakPoints),
    JSON.stringify(profile.recentStates),
    JSON.stringify(profile.effectiveStrategies),
    profile.learningSummary,
    profile.totalSessions,
    profile.updatedAt
  );
}

function upsertKnowledgePoint(
  db: DatabaseSync,
  point: (typeof seedKnowledgePoints)[number]
): void {
  db.prepare(
    `INSERT INTO knowledge_point (id, name, subject, chapter, parent_id)
     VALUES (?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       name = excluded.name,
       subject = excluded.subject,
       chapter = excluded.chapter,
       parent_id = excluded.parent_id`
  ).run(point.id, point.name, point.subject, point.chapter, point.parentId);
}

function upsertStudentKnowledge(
  db: DatabaseSync,
  record: (typeof seedStudentKnowledge)[number]
): void {
  db.prepare(
    `INSERT INTO student_knowledge (
       id, student_id, knowledge_point_id, mastery, attempts, correct_count, last_practiced_at
     )
     VALUES (?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       student_id = excluded.student_id,
       knowledge_point_id = excluded.knowledge_point_id,
       mastery = excluded.mastery,
       attempts = excluded.attempts,
       correct_count = excluded.correct_count,
       last_practiced_at = excluded.last_practiced_at`
  ).run(
    record.id,
    record.studentId,
    record.knowledgePointId,
    record.mastery,
    record.attempts,
    record.correctCount,
    record.lastPracticedAt
  );
}

function upsertQuestion(db: DatabaseSync, question: (typeof seedQuestions)[number]): void {
  db.prepare(
    `INSERT INTO question (
       id, stem, standard_answer, solution, difficulty,
       typical_errors, visual_aid_type, visual_aid_spec
     )
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       stem = excluded.stem,
       standard_answer = excluded.standard_answer,
       solution = excluded.solution,
       difficulty = excluded.difficulty,
       typical_errors = excluded.typical_errors,
       visual_aid_type = excluded.visual_aid_type,
       visual_aid_spec = excluded.visual_aid_spec`
  ).run(
    question.id,
    question.stem,
    question.standardAnswer,
    question.solution,
    question.difficulty,
    JSON.stringify(question.typicalErrors),
    question.visualAidType,
    question.visualAidSpec === null ? null : JSON.stringify(question.visualAidSpec)
  );
}

function upsertQuestionKnowledge(
  db: DatabaseSync,
  record: (typeof seedQuestionKnowledge)[number]
): void {
  db.prepare(
    `INSERT INTO question_knowledge (id, question_id, knowledge_point_id)
     VALUES (?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
       question_id = excluded.question_id,
       knowledge_point_id = excluded.knowledge_point_id`
  ).run(record.id, record.questionId, record.knowledgePointId);
}

function isDirectRun(): boolean {
  const entry = process.argv[1];

  return Boolean(entry && import.meta.url === pathToFileURL(entry).href);
}

if (isDirectRun()) {
  console.log(JSON.stringify(seedDatabase(), null, 2));
}
