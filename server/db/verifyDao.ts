import assert from "node:assert/strict";
import { createDatabaseConnection } from "./connection.js";
import {
  getKnowledgePointById,
  getLearningEventById,
  getQuestionById,
  getQuestionKnowledgeById,
  getReviewTaskById,
  getSessionById,
  getStudentById,
  getStudentKnowledgeById,
  getStudentProfileById,
  insertKnowledgePoint,
  insertLearningEvent,
  insertQuestion,
  insertQuestionKnowledge,
  insertReviewTask,
  insertSession,
  insertStudent,
  insertStudentKnowledge,
  insertStudentProfile
} from "./index.js";

const db = createDatabaseConnection(":memory:");
const now = "2026-05-27T00:00:00Z";

function expectForeignKeyFailure(run: () => void): void {
  assert.throws(run, /FOREIGN KEY constraint failed/);
}

insertStudent(
  {
    id: "stu_verify",
    name: "验证学生",
    grade: "高一",
    createdAt: now
  },
  db
);

insertStudentProfile(
  {
    id: "profile_verify",
    studentId: "stu_verify",
    weakPoints: ["kp_verify"],
    recentStates: ["confused"],
    effectiveStrategies: ["small_step"],
    learningSummary: "容易在二次函数最值题中卡住。",
    totalSessions: 1,
    updatedAt: now
  },
  db
);

insertKnowledgePoint(
  {
    id: "kp_verify",
    name: "二次函数最值",
    subject: "math",
    chapter: "函数",
    parentId: null
  },
  db
);

insertStudentKnowledge(
  {
    id: "sk_verify",
    studentId: "stu_verify",
    knowledgePointId: "kp_verify",
    mastery: 52,
    attempts: 3,
    correctCount: 1,
    lastPracticedAt: now
  },
  db
);

insertQuestion(
  {
    id: "q_verify",
    stem: "求函数 y=x^2-2x 在 [0,3] 上的最小值。",
    standardAnswer: "-1",
    solution: "配方得 y=(x-1)^2-1，x=1 在区间内，所以最小值为 -1。",
    difficulty: "medium",
    typicalErrors: [{ cause: "concept", detail: "忽略顶点是否在给定区间内。" }],
    visualAidType: "function_graph",
    visualAidSpec: {
      expression: "x^2-2x",
      xRange: [0, 3],
      highlightX: 1
    }
  },
  db
);

insertQuestionKnowledge(
  {
    id: "qk_verify",
    questionId: "q_verify",
    knowledgePointId: "kp_verify"
  },
  db
);

insertSession(
  {
    id: "sess_verify",
    studentId: "stu_verify",
    startedAt: now,
    endedAt: null,
    dominantState: null,
    summary: null,
    eventCount: 0
  },
  db
);

insertLearningEvent(
  {
    id: "evt_verify",
    sessionId: "sess_verify",
    studentId: "stu_verify",
    questionId: "q_verify",
    sequence: 1,
    studentInput: "我觉得最小值是 0。",
    studentAnswer: "0",
    isCorrect: false,
    knowledgePointIds: ["kp_verify"],
    errorCause: "concept",
    errorDetail: "没有把二次函数顶点纳入区间判断。",
    state: "confused",
    stateEvidence: "学生给出错误答案并表达不确定。",
    strategy: ["hint", "small_step"],
    strategyReason: "该生仍在尝试，先给关键提示再拆小步。",
    careTriggered: false,
    visualAidUsed: "function_graph",
    tutorResponse: "我们先看顶点 x=1 有没有落在区间里。",
    createdAt: now
  },
  db
);

insertReviewTask(
  {
    id: "rt_verify",
    studentId: "stu_verify",
    knowledgePointId: "kp_verify",
    sourceEventId: "evt_verify",
    reason: "二次函数最值题出现概念性错误。",
    recommendedQuestionId: "q_verify",
    status: "pending",
    dueDate: "2026-05-28",
    createdAt: now
  },
  db
);

assert.equal(getStudentById("stu_verify", db)?.name, "验证学生");
assert.equal(getStudentProfileById("profile_verify", db)?.weakPoints[0], "kp_verify");
assert.equal(getKnowledgePointById("kp_verify", db)?.name, "二次函数最值");
assert.equal(getStudentKnowledgeById("sk_verify", db)?.mastery, 52);
assert.equal(getQuestionById("q_verify", db)?.typicalErrors[0]?.cause, "concept");
assert.equal(getQuestionKnowledgeById("qk_verify", db)?.questionId, "q_verify");
assert.equal(getSessionById("sess_verify", db)?.studentId, "stu_verify");
assert.equal(getLearningEventById("evt_verify", db)?.strategy[1], "small_step");
assert.equal(getReviewTaskById("rt_verify", db)?.status, "pending");

expectForeignKeyFailure(() => {
  insertStudentKnowledge(
    {
      id: "sk_bad_fk",
      studentId: "missing_student",
      knowledgePointId: "kp_verify",
      mastery: 50,
      attempts: 0,
      correctCount: 0,
      lastPracticedAt: null
    },
    db
  );
});

const foreignKeyProblems = db.prepare("PRAGMA foreign_key_check").all();
assert.deepEqual(foreignKeyProblems, []);

db.close();

console.log("T1-1 DAO 验证通过：9 张表均可增查，外键约束生效。");
