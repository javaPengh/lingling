PRAGMA foreign_keys = ON;

-- 学生基础信息表：只放最小身份信息；登录凭据属于 account 表。
CREATE TABLE IF NOT EXISTS student (
  id          TEXT PRIMARY KEY, -- 学生 ID，种子数据建议用 stu_001 这类可读短码。
  name        TEXT NOT NULL,    -- 学生昵称/姓名，例如“小宇”。
  grade       TEXT NOT NULL,    -- 年级，例如“高一”。
  created_at  TEXT NOT NULL     -- 创建时间，ISO 8601 字符串。
);

-- 账号表：表达登录入口中的“谁以什么角色进入系统”。
-- V0.1 使用预置账号密码登录，不做注册、找回、token 持久会话等完整账号体系。
CREATE TABLE IF NOT EXISTS account (
  id            TEXT PRIMARY KEY, -- 账号 ID，例如 acc_stu_001。
  username      TEXT NOT NULL UNIQUE, -- 登录账号名，例如 xiaoyu。
  password_hash TEXT NOT NULL,    -- 密码哈希；不存明文密码。
  role          TEXT NOT NULL CHECK (role IN ('student','parent','teacher')), -- 角色：student / parent / teacher。
  display_name  TEXT NOT NULL,    -- 登录入口展示名称，例如“小宇”“小宇的家长”“王老师”。
  student_id    TEXT,             -- 仅学生账号有值，指向该账号对应的学生本人。
  created_at    TEXT NOT NULL,    -- 账号创建时间，ISO 8601 字符串。
  FOREIGN KEY (student_id) REFERENCES student(id)
);

-- 账号-学生关联表：表达家长/老师账号能查看哪些学生。
-- 学生账号本人不依赖此表，而是通过 account.student_id 指向本人。
CREATE TABLE IF NOT EXISTS account_student (
  id          TEXT PRIMARY KEY, -- 关联记录 ID。
  account_id  TEXT NOT NULL,    -- 家长或老师账号 ID。
  student_id  TEXT NOT NULL,    -- 该账号有权查看的学生 ID。
  UNIQUE (account_id, student_id),
  FOREIGN KEY (account_id) REFERENCES account(id),
  FOREIGN KEY (student_id) REFERENCES student(id)
);

-- 学生画像表：长期记忆的文字/标签部分，与 student 一对一。
CREATE TABLE IF NOT EXISTS student_profile (
  id                    TEXT PRIMARY KEY,           -- 画像 ID。
  student_id            TEXT NOT NULL UNIQUE,       -- 对应的学生 ID；一个学生只有一份画像。
  weak_points           TEXT,                       -- JSON 数组：薄弱知识点 ID，如 ["kp_003"]。
  recent_states         TEXT,                       -- JSON 数组：近期学习状态，如 ["frustrated","confused"]。
  effective_strategies  TEXT,                       -- JSON 数组：对该学生有效的策略，如 ["small_step","humor"]。
  learning_summary      TEXT,                       -- 自然语言长期画像摘要，给提示词和报告使用。
  total_sessions        INTEGER NOT NULL DEFAULT 0, -- 累计学习会话次数。
  updated_at            TEXT NOT NULL,              -- 画像最近更新时间。
  FOREIGN KEY (student_id) REFERENCES student(id)
);

-- 知识点字典表：高中数学知识点的基础目录，题目和掌握度都挂在这里。
CREATE TABLE IF NOT EXISTS knowledge_point (
  id         TEXT PRIMARY KEY, -- 知识点 ID，例如 kp_001。
  name       TEXT NOT NULL,    -- 知识点名称，例如“二次函数最值”。
  subject    TEXT NOT NULL,    -- 学科，V0.1 固定为 math。
  chapter    TEXT,             -- 所属章节，例如“函数”。
  parent_id  TEXT,             -- 上位知识点 ID，可为空，用于简单层级。
  FOREIGN KEY (parent_id) REFERENCES knowledge_point(id)
);

-- 学生知识点掌握度表：长期记忆的量化部分，记录某学生对某知识点掌握到什么程度。
CREATE TABLE IF NOT EXISTS student_knowledge (
  id                  TEXT PRIMARY KEY,                              -- 掌握度记录 ID。
  student_id          TEXT NOT NULL,                                 -- 学生 ID。
  knowledge_point_id  TEXT NOT NULL,                                 -- 知识点 ID。
  mastery             INTEGER NOT NULL CHECK (mastery BETWEEN 0 AND 100), -- 掌握度分数，0-100。
  attempts            INTEGER NOT NULL DEFAULT 0,                    -- 该知识点累计作答次数。
  correct_count       INTEGER NOT NULL DEFAULT 0,                    -- 该知识点累计答对次数。
  last_practiced_at   TEXT,                                          -- 最近练习该知识点的时间。
  UNIQUE (student_id, knowledge_point_id),
  FOREIGN KEY (student_id) REFERENCES student(id),
  FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_point(id)
);

-- 题库表：预置演示题目。深图模块用它判题、归因，前端用它展示题目和画图参数。
CREATE TABLE IF NOT EXISTS question (
  id               TEXT PRIMARY KEY, -- 题目 ID，例如 q_001。
  stem             TEXT NOT NULL,    -- 题干文本，可包含基础数学符号或 LaTeX。
  standard_answer  TEXT NOT NULL,    -- 标准答案。
  solution         TEXT NOT NULL,    -- 标准解题步骤，给灵灵兜底讲解用。
  difficulty       TEXT NOT NULL CHECK (difficulty IN ('easy','medium','hard')), -- 难度：easy / medium / hard。
  typical_errors   TEXT,             -- JSON 数组：本题典型错因，如 [{"cause":"concept","detail":"..."}]。
  visual_aid_type  TEXT NOT NULL DEFAULT 'none', -- 建议画图类型：none / function_graph / geometry 等。
  visual_aid_spec  TEXT              -- JSON 对象：画图参数，例如函数表达式、坐标范围、高亮区间。
);

-- 题目-知识点关联表：一题可以对应多个知识点，一个知识点也可以出现在多题中。
CREATE TABLE IF NOT EXISTS question_knowledge (
  id                  TEXT PRIMARY KEY, -- 关联记录 ID。
  question_id         TEXT NOT NULL,    -- 题目 ID。
  knowledge_point_id  TEXT NOT NULL,    -- 知识点 ID。
  UNIQUE (question_id, knowledge_point_id),
  FOREIGN KEY (question_id) REFERENCES question(id),
  FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_point(id)
);

-- 学习会话表：一次从开始学习到点击结束/复盘的完整过程。
CREATE TABLE IF NOT EXISTS session (
  id              TEXT PRIMARY KEY,           -- 会话 ID，例如 sess_001。
  student_id      TEXT NOT NULL,              -- 本次会话对应的学生 ID。
  started_at      TEXT NOT NULL,              -- 会话开始时间。
  ended_at        TEXT,                       -- 会话结束时间；进行中为空。
  dominant_state  TEXT,                       -- 本次会话主导状态，如 confused / frustrated。
  summary         TEXT,                       -- 本次学习复盘摘要。
  event_count     INTEGER NOT NULL DEFAULT 0, -- 本会话累计学习事件数。
  FOREIGN KEY (student_id) REFERENCES student(id)
);

-- 学习事件表：最核心的表。每一轮“学生输入 -> 系统判断 -> 灵灵回应”都写一条。
-- 观察面板主要就是把这张表里的状态、证据、策略、原因、关怀和画图记录展示出来。
CREATE TABLE IF NOT EXISTS learning_event (
  id                   TEXT PRIMARY KEY, -- 事件 ID，例如 evt_001。
  session_id           TEXT NOT NULL,    -- 所属会话 ID。
  student_id           TEXT NOT NULL,    -- 学生 ID，冗余保存便于跨会话查询。
  question_id          TEXT,             -- 本轮关联题目 ID；自由提问时可为空。
  sequence             INTEGER NOT NULL, -- 本会话内第几轮，从 1 开始递增。
  student_input        TEXT,             -- 学生本轮输入原文。
  student_answer       TEXT,             -- 如果本轮是作答，这里记录答案；追问/闲聊可为空。
  is_correct           INTEGER,          -- 是否答对：1 对，0 错，非作答为空。
  knowledge_point_ids  TEXT,             -- JSON 数组：本轮命中的知识点 ID。
  error_cause          TEXT CHECK (error_cause IN
                         ('calculation','concept','misread','method',
                          'incomplete','careless','unknown') OR error_cause IS NULL), -- 错因分类；答对或无错为空。
  error_detail         TEXT, -- 错因的自然语言说明，例如“忘记讨论参数范围”。
  state                TEXT NOT NULL CHECK (state IN
                         ('stable','confused','frustrated','tired','anxious')), -- 本轮学习状态。
  state_evidence       TEXT NOT NULL,             -- 识别该状态的证据，观察面板必须展示。
  strategy             TEXT NOT NULL,             -- JSON 数组：采用的教学策略，如 ["care","small_step"]。
  strategy_reason      TEXT NOT NULL,             -- 为什么选这些策略，观察面板必须展示。
  care_triggered       INTEGER NOT NULL DEFAULT 0, -- 是否触发主动关怀：1 是，0 否。
  visual_aid_used      TEXT NOT NULL DEFAULT 'none', -- 本轮实际使用的画图/视觉辅助类型。
  tutor_response       TEXT NOT NULL,             -- 灵灵本轮回复原文。
  created_at           TEXT NOT NULL,             -- 事件创建时间。
  FOREIGN KEY (session_id) REFERENCES session(id),
  FOREIGN KEY (student_id) REFERENCES student(id),
  FOREIGN KEY (question_id) REFERENCES question(id)
);

-- 复习任务表：会话结束后生成的主动复习任务，证明系统把本次学习沉淀成后续安排。
CREATE TABLE IF NOT EXISTS review_task (
  id                      TEXT PRIMARY KEY, -- 复习任务 ID。
  student_id              TEXT NOT NULL,    -- 学生 ID。
  knowledge_point_id      TEXT NOT NULL,    -- 要复习的薄弱知识点 ID。
  source_event_id         TEXT,             -- 触发该任务的学习事件 ID，可为空。
  reason                  TEXT NOT NULL,    -- 生成原因，例如“二次函数最值连续答错 2 次”。
  recommended_question_id TEXT,             -- 推荐复习题 ID，可为空。
  status                  TEXT NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending','done','skipped')), -- 状态：pending / done / skipped。
  due_date                TEXT,          -- 建议复习日期。
  created_at              TEXT NOT NULL, -- 创建时间。
  FOREIGN KEY (student_id) REFERENCES student(id),
  FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_point(id),
  FOREIGN KEY (source_event_id) REFERENCES learning_event(id),
  FOREIGN KEY (recommended_question_id) REFERENCES question(id)
);
