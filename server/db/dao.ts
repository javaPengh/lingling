import type { StudentSummary } from "../../shared/api.js";
import { getDatabase } from "./connection.js";

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
