import { dbOrDefault, type Db } from "./sqliteHelpers.js";
import type { KnowledgePoint } from "../types/entities.js";

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
