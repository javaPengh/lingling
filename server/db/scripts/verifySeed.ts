import assert from "node:assert/strict";
import type { DatabaseSync } from "node:sqlite";
import { createDatabaseConnection } from "../connection.js";
import {
  getQuestionById,
  getStudentProfileByStudentId,
  listStudents
} from "../index.js";
import { seedDatabase } from "./seed.js";

const db = createDatabaseConnection(":memory:");

seedDatabase(db);
seedDatabase(db);

assert.equal(countRows(db, "student"), 3);
assert.equal(countRows(db, "student_profile"), 3);
assert.equal(countRows(db, "knowledge_point"), 9);
assert.equal(countRows(db, "student_knowledge"), 13);
assert.equal(countRows(db, "question"), 7);
assert.equal(countRows(db, "question_knowledge"), 10);

const students = listStudents(db);
assert.deepEqual(
  students.map((student) => student.name),
  ["小宇", "小哲", "小琳"]
);

const xiaoyuProfile = getStudentProfileByStudentId("stu_001", db);
assert.deepEqual(xiaoyuProfile?.weakPoints, ["kp_003", "kp_004"]);
assert.equal(xiaoyuProfile?.effectiveStrategies.includes("small_step"), true);

const mainQuestion = getQuestionById("q_001", db);
assert.equal(mainQuestion?.visualAidType, "function_graph");
assert.equal(mainQuestion?.typicalErrors[0]?.cause, "concept");

const geometryQuestion = getQuestionById("q_006", db);
assert.equal(geometryQuestion?.visualAidType, "geometry");

const foreignKeyProblems = db.prepare("PRAGMA foreign_key_check").all();
assert.deepEqual(foreignKeyProblems, []);

db.close();

console.log("T1-3 seed 验证通过：3 个学生、9 个知识点、7 道题均已写入且可重复执行。");

function countRows(db: DatabaseSync, table: string): number {
  const row = db.prepare(`SELECT COUNT(*) AS count FROM ${table}`).get() as { count: number };

  return row.count;
}
