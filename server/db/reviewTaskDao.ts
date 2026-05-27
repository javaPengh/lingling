import { dbOrDefault, type Db } from "./sqliteHelpers.js";
import type { ReviewStatus, ReviewTask } from "./types.js";

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
