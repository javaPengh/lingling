import type { VisualAidType } from "../../../shared/api.js";
import {
  dbOrDefault,
  jsonText,
  nullableJsonText,
  parseJson,
  type Db
} from "./sqliteHelpers.js";
import type { Difficulty, JsonRecord, Question, QuestionKnowledge, TypicalError } from "../types/entities.js";

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
