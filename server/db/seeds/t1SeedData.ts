import type {
  KnowledgePoint,
  Question,
  QuestionKnowledge,
  Student,
  StudentKnowledge,
  StudentProfile
} from "../types/entities.js";

export const seedStudents: Student[] = [
  {
    id: "stu_001",
    name: "小宇",
    grade: "高一",
    createdAt: "2026-05-01T08:00:00Z"
  },
  {
    id: "stu_002",
    name: "小琳",
    grade: "高一",
    createdAt: "2026-05-03T08:00:00Z"
  },
  {
    id: "stu_003",
    name: "小哲",
    grade: "高一",
    createdAt: "2026-05-02T08:00:00Z"
  }
];

export const seedStudentProfiles: StudentProfile[] = [
  {
    id: "profile_stu_001",
    studentId: "stu_001",
    weakPoints: ["kp_003", "kp_004"],
    recentStates: ["confused", "frustrated", "frustrated"],
    effectiveStrategies: ["small_step", "humor"],
    learningSummary:
      "小宇基础尚可，但一遇含参/分类讨论就容易卡，受挫后易说「我不会」放弃。拆小步引导和轻松氛围对他效果好。",
    totalSessions: 3,
    updatedAt: "2026-05-20T20:00:00Z"
  },
  {
    id: "profile_stu_002",
    studentId: "stu_002",
    weakPoints: ["kp_008"],
    recentStates: ["anxious", "stable", "anxious"],
    effectiveStrategies: ["care", "hint"],
    learningSummary:
      "小琳基础其实不弱，但极在意分数与考试，一紧张就乱、爱说「来不及了」「会不会考」。需要先安抚情绪、给确定感，再推进；对她不宜用调侃式幽默。",
    totalSessions: 5,
    updatedAt: "2026-05-21T19:00:00Z"
  },
  {
    id: "profile_stu_003",
    studentId: "stu_003",
    weakPoints: [],
    recentStates: ["stable", "stable", "stable"],
    effectiveStrategies: ["socratic"],
    learningSummary:
      "小哲基础扎实、肯钻研、情绪稳定，主要问题是偶尔粗心（看错条件、笔误）。适合用追问引导他自查与延展拔高，不需要额外关怀安抚。",
    totalSessions: 6,
    updatedAt: "2026-05-21T20:00:00Z"
  }
];

export const seedKnowledgePoints: KnowledgePoint[] = [
  {
    id: "kp_001",
    name: "函数",
    subject: "math",
    chapter: "函数",
    parentId: null
  },
  {
    id: "kp_002",
    name: "二次函数",
    subject: "math",
    chapter: "函数",
    parentId: "kp_001"
  },
  {
    id: "kp_003",
    name: "二次函数最值",
    subject: "math",
    chapter: "函数",
    parentId: "kp_002"
  },
  {
    id: "kp_004",
    name: "含参讨论",
    subject: "math",
    chapter: "函数",
    parentId: "kp_002"
  },
  {
    id: "kp_005",
    name: "一元二次方程与判别式",
    subject: "math",
    chapter: "方程",
    parentId: null
  },
  {
    id: "kp_006",
    name: "集合运算",
    subject: "math",
    chapter: "集合",
    parentId: null
  },
  {
    id: "kp_007",
    name: "不等式求解",
    subject: "math",
    chapter: "不等式",
    parentId: null
  },
  {
    id: "kp_008",
    name: "立体几何（空间想象）",
    subject: "math",
    chapter: "立体几何",
    parentId: null
  },
  {
    id: "kp_009",
    name: "概率（古典概型）",
    subject: "math",
    chapter: "概率",
    parentId: null
  }
];

export const seedStudentKnowledge: StudentKnowledge[] = [
  makeStudentKnowledge("stu_001", "kp_003", 52, 6, 3),
  makeStudentKnowledge("stu_001", "kp_004", 45, 4, 1),
  makeStudentKnowledge("stu_001", "kp_002", 70, 8, 6),
  makeStudentKnowledge("stu_001", "kp_005", 65, 5, 4),
  makeStudentKnowledge("stu_001", "kp_006", 80, 4, 4),
  makeStudentKnowledge("stu_002", "kp_008", 48, 5, 2),
  makeStudentKnowledge("stu_002", "kp_003", 72, 6, 5),
  makeStudentKnowledge("stu_002", "kp_005", 75, 5, 4),
  makeStudentKnowledge("stu_002", "kp_006", 82, 4, 4),
  makeStudentKnowledge("stu_003", "kp_003", 88, 7, 7),
  makeStudentKnowledge("stu_003", "kp_005", 90, 6, 6),
  makeStudentKnowledge("stu_003", "kp_006", 85, 5, 5),
  makeStudentKnowledge("stu_003", "kp_009", 78, 4, 3)
];

export const seedQuestions: Question[] = [
  {
    id: "q_001",
    stem: "已知函数 f(x)=x²−2ax+1，求 f(x) 在区间 [0,2] 上的最小值（用 a 表示）。",
    standardAnswer: "a<0 时最小值 f(0)=1；0≤a≤2 时 f(a)=1−a²；a>2 时 f(2)=5−4a。",
    solution:
      "对称轴 x=a。①a<0：f 在[0,2]递增，最小值 f(0)=1。②0≤a≤2：顶点在区间内，最小值 f(a)=1−a²。③a>2：f 递减，最小值 f(2)=5−4a。",
    difficulty: "hard",
    typicalErrors: [
      {
        cause: "concept",
        detail: "忽略对称轴位置，直接代端点或顶点，未分类讨论"
      },
      {
        cause: "incomplete",
        detail: "只讨论部分情况，漏掉a<0或a>2"
      }
    ],
    visualAidType: "function_graph",
    visualAidSpec: {
      expr: "x^2-2*a*x+1",
      param: "a",
      x_range: [-1, 3],
      highlight_interval: [0, 2],
      show_axis_of_symmetry: true
    }
  },
  {
    id: "q_002",
    stem: "求二次函数 f(x)=x²−4x+5 的最小值。",
    standardAnswer: "最小值为 1（在 x=2 处取得）。",
    solution: "配方 f(x)=(x−2)²+1，顶点 (2,1)，开口向上，最小值 1。",
    difficulty: "easy",
    typicalErrors: [
      {
        cause: "calculation",
        detail: "配方时常数项算错"
      },
      {
        cause: "concept",
        detail: "误把对称轴x值当成最小值"
      }
    ],
    visualAidType: "function_graph",
    visualAidSpec: {
      expr: "x^2-4*x+5",
      x_range: [-1, 5],
      mark_vertex: true
    }
  },
  {
    id: "q_003",
    stem: "若关于 x 的方程 x²−2x+m=0 有两个不相等的实数根，求 m 的取值范围。",
    standardAnswer: "m<1。",
    solution: "两个不相等实根需判别式 Δ>0，即 4−4m>0，解得 m<1。",
    difficulty: "medium",
    typicalErrors: [
      {
        cause: "concept",
        detail: "混淆Δ>0与Δ≥0"
      },
      {
        cause: "calculation",
        detail: "判别式符号或移项出错"
      }
    ],
    visualAidType: "none",
    visualAidSpec: null
  },
  {
    id: "q_004",
    stem: "已知集合 A={x | −1<x≤3}，B={x | x≥2}，求 A∩B。",
    standardAnswer: "A∩B={x | 2≤x≤3}。",
    solution: "取两集合公共部分，下界取较大者 2（含），上界取较小者 3（含）。",
    difficulty: "easy",
    typicalErrors: [
      {
        cause: "careless",
        detail: "端点开闭弄反"
      },
      {
        cause: "misread",
        detail: "把交集做成并集"
      }
    ],
    visualAidType: "diagram",
    visualAidSpec: {
      type: "number_line",
      sets: [
        {
          name: "A",
          range: [-1, 3],
          open: [true, false]
        },
        {
          name: "B",
          range: [2, "inf"],
          open: [false, false]
        }
      ]
    }
  },
  {
    id: "q_005",
    stem: "已知函数 f(x)=x²−2ax+1 在区间 [1,3] 上单调递增，求 a 的取值范围。",
    standardAnswer: "a≤1。",
    solution: "对称轴 x=a，开口向上，在[1,3]递增需对称轴在区间左侧或左端点，即 a≤1。",
    difficulty: "medium",
    typicalErrors: [
      {
        cause: "concept",
        detail: "单调性与对称轴位置关系判断错"
      },
      {
        cause: "incomplete",
        detail: "漏掉a=1的边界"
      }
    ],
    visualAidType: "function_graph",
    visualAidSpec: {
      expr: "x^2-2*a*x+1",
      param: "a",
      x_range: [0, 4],
      highlight_interval: [1, 3]
    }
  },
  {
    id: "q_006",
    stem: "正方体 ABCD-A₁B₁C₁D₁ 的棱长为 2，求异面直线 AC 与 BD₁ 所成角的余弦值。",
    standardAnswer: "余弦值为 √3/3。",
    solution:
      "建空间直角坐标系，设各顶点坐标，求向量 AC 与 BD₁ 夹角余弦：数量积除以模长之积，得 √3/3。",
    difficulty: "hard",
    typicalErrors: [
      {
        cause: "concept",
        detail: "异面直线所成角与向量夹角取绝对值处理混淆"
      },
      {
        cause: "method",
        detail: "不会建系，凭空想象导致卡住"
      }
    ],
    visualAidType: "geometry",
    visualAidSpec: {
      type: "cube",
      edge: 2,
      label_vertices: true,
      highlight_lines: ["AC", "BD1"]
    }
  },
  {
    id: "q_007",
    stem: "从 1,2,3,4,5 中任取两个不同的数，求两数之和为偶数的概率。",
    standardAnswer: "2/5。",
    solution:
      "总取法 C(5,2)=10；和为偶数需两数同奇偶：奇{1,3,5}取两个 C(3,2)=3，偶{2,4}取两个 C(2,2)=1，共 4 种；概率 4/10=2/5。",
    difficulty: "medium",
    typicalErrors: [
      {
        cause: "careless",
        detail: "漏算偶数对或重复计数"
      },
      {
        cause: "concept",
        detail: "误用排列A而非组合C"
      }
    ],
    visualAidType: "none",
    visualAidSpec: null
  }
];

export const seedQuestionKnowledge: QuestionKnowledge[] = [
  { id: "qk_001_003", questionId: "q_001", knowledgePointId: "kp_003" },
  { id: "qk_001_004", questionId: "q_001", knowledgePointId: "kp_004" },
  { id: "qk_002_003", questionId: "q_002", knowledgePointId: "kp_003" },
  { id: "qk_003_005", questionId: "q_003", knowledgePointId: "kp_005" },
  { id: "qk_003_007", questionId: "q_003", knowledgePointId: "kp_007" },
  { id: "qk_004_006", questionId: "q_004", knowledgePointId: "kp_006" },
  { id: "qk_005_004", questionId: "q_005", knowledgePointId: "kp_004" },
  { id: "qk_005_003", questionId: "q_005", knowledgePointId: "kp_003" },
  { id: "qk_006_008", questionId: "q_006", knowledgePointId: "kp_008" },
  { id: "qk_007_009", questionId: "q_007", knowledgePointId: "kp_009" }
];

function makeStudentKnowledge(
  studentId: string,
  knowledgePointId: string,
  mastery: number,
  attempts: number,
  correctCount: number
): StudentKnowledge {
  return {
    id: `sk_${studentId.slice(-3)}_${knowledgePointId.slice(-3)}`,
    studentId,
    knowledgePointId,
    mastery,
    attempts,
    correctCount,
    lastPracticedAt: "2026-05-21T12:00:00Z"
  };
}
