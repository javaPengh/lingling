PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS student (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  grade       TEXT NOT NULL,
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS student_profile (
  id                    TEXT PRIMARY KEY,
  student_id            TEXT NOT NULL UNIQUE,
  weak_points           TEXT,
  recent_states         TEXT,
  effective_strategies  TEXT,
  learning_summary      TEXT,
  total_sessions        INTEGER NOT NULL DEFAULT 0,
  updated_at            TEXT NOT NULL,
  FOREIGN KEY (student_id) REFERENCES student(id)
);

CREATE TABLE IF NOT EXISTS knowledge_point (
  id         TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  subject    TEXT NOT NULL,
  chapter    TEXT,
  parent_id  TEXT,
  FOREIGN KEY (parent_id) REFERENCES knowledge_point(id)
);

CREATE TABLE IF NOT EXISTS student_knowledge (
  id                  TEXT PRIMARY KEY,
  student_id          TEXT NOT NULL,
  knowledge_point_id  TEXT NOT NULL,
  mastery             INTEGER NOT NULL CHECK (mastery BETWEEN 0 AND 100),
  attempts            INTEGER NOT NULL DEFAULT 0,
  correct_count       INTEGER NOT NULL DEFAULT 0,
  last_practiced_at   TEXT,
  UNIQUE (student_id, knowledge_point_id),
  FOREIGN KEY (student_id) REFERENCES student(id),
  FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_point(id)
);

CREATE TABLE IF NOT EXISTS question (
  id               TEXT PRIMARY KEY,
  stem             TEXT NOT NULL,
  standard_answer  TEXT NOT NULL,
  solution         TEXT NOT NULL,
  difficulty       TEXT NOT NULL CHECK (difficulty IN ('easy','medium','hard')),
  typical_errors   TEXT,
  visual_aid_type  TEXT NOT NULL DEFAULT 'none',
  visual_aid_spec  TEXT
);

CREATE TABLE IF NOT EXISTS question_knowledge (
  id                  TEXT PRIMARY KEY,
  question_id         TEXT NOT NULL,
  knowledge_point_id  TEXT NOT NULL,
  UNIQUE (question_id, knowledge_point_id),
  FOREIGN KEY (question_id) REFERENCES question(id),
  FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_point(id)
);

CREATE TABLE IF NOT EXISTS session (
  id              TEXT PRIMARY KEY,
  student_id      TEXT NOT NULL,
  started_at      TEXT NOT NULL,
  ended_at        TEXT,
  dominant_state  TEXT,
  summary         TEXT,
  event_count     INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (student_id) REFERENCES student(id)
);

CREATE TABLE IF NOT EXISTS learning_event (
  id                   TEXT PRIMARY KEY,
  session_id           TEXT NOT NULL,
  student_id           TEXT NOT NULL,
  question_id          TEXT,
  sequence             INTEGER NOT NULL,
  student_input        TEXT,
  student_answer       TEXT,
  is_correct           INTEGER,
  knowledge_point_ids  TEXT,
  error_cause          TEXT CHECK (error_cause IN
                         ('calculation','concept','misread','method',
                          'incomplete','careless','unknown') OR error_cause IS NULL),
  error_detail         TEXT,
  state                TEXT NOT NULL CHECK (state IN
                         ('stable','confused','frustrated','tired','anxious')),
  state_evidence       TEXT NOT NULL,
  strategy             TEXT NOT NULL,
  strategy_reason      TEXT NOT NULL,
  care_triggered       INTEGER NOT NULL DEFAULT 0,
  visual_aid_used      TEXT NOT NULL DEFAULT 'none',
  tutor_response       TEXT NOT NULL,
  created_at           TEXT NOT NULL,
  FOREIGN KEY (session_id) REFERENCES session(id),
  FOREIGN KEY (student_id) REFERENCES student(id),
  FOREIGN KEY (question_id) REFERENCES question(id)
);

CREATE TABLE IF NOT EXISTS review_task (
  id                      TEXT PRIMARY KEY,
  student_id              TEXT NOT NULL,
  knowledge_point_id      TEXT NOT NULL,
  source_event_id         TEXT,
  reason                  TEXT NOT NULL,
  recommended_question_id TEXT,
  status                  TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending','done','skipped')),
  due_date                TEXT,
  created_at              TEXT NOT NULL,
  FOREIGN KEY (student_id) REFERENCES student(id),
  FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_point(id),
  FOREIGN KEY (source_event_id) REFERENCES learning_event(id),
  FOREIGN KEY (recommended_question_id) REFERENCES question(id)
);
