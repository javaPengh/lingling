"""种子数据脚本。

把《种子数据与演示脚本》中的三名学生、知识点、题库和初始掌握度写入 SQLite。
脚本使用 upsert，重复执行不会产生重复数据。
"""

from __future__ import annotations

from sqlite3 import Connection

from server.core.security import hash_password
from server.dao.connection import create_connection
from server.dao.account_dao import upsert_account, upsert_account_student
from server.dao.knowledge_dao import upsert_knowledge_point
from server.dao.question_dao import upsert_question, upsert_question_knowledge
from server.dao.student_dao import upsert_student, upsert_student_knowledge, upsert_student_profile
from server.models.entities import (
    Account,
    AccountStudent,
    KnowledgePoint,
    Question,
    QuestionKnowledge,
    Student,
    StudentKnowledge,
    StudentProfile,
)


SEED_STUDENTS = [
    {"id": "stu_001", "name": "小宇", "grade": "高一", "created_at": "2026-05-01T08:00:00Z"},
    {"id": "stu_002", "name": "小琳", "grade": "高一", "created_at": "2026-05-03T08:00:00Z"},
    {"id": "stu_003", "name": "小哲", "grade": "高一", "created_at": "2026-05-02T08:00:00Z"},
]

DEMO_LOGIN_PASSWORD = "123456"


def demo_password_hash(account_id: str) -> str:
    """生成演示账号的稳定密码哈希，便于种子数据重复执行。"""

    return hash_password(DEMO_LOGIN_PASSWORD, salt=f"lingling-demo:{account_id}")


SEED_ACCOUNTS = [
    {
        "id": "acc_stu_001",
        "username": "xiaoyu",
        "password_hash": demo_password_hash("acc_stu_001"),
        "role": "student",
        "display_name": "小宇",
        "student_id": "stu_001",
        "created_at": "2026-05-01T08:10:00Z",
    },
    {
        "id": "acc_stu_002",
        "username": "xiaozhe",
        "password_hash": demo_password_hash("acc_stu_002"),
        "role": "student",
        "display_name": "小哲",
        "student_id": "stu_003",
        "created_at": "2026-05-01T08:20:00Z",
    },
    {
        "id": "acc_stu_003",
        "username": "xiaolin",
        "password_hash": demo_password_hash("acc_stu_003"),
        "role": "student",
        "display_name": "小琳",
        "student_id": "stu_002",
        "created_at": "2026-05-01T08:30:00Z",
    },
    {
        "id": "acc_parent_001",
        "username": "parent_xiaoyu",
        "password_hash": demo_password_hash("acc_parent_001"),
        "role": "parent",
        "display_name": "小宇的家长",
        "student_id": None,
        "created_at": "2026-05-01T08:40:00Z",
    },
    {
        "id": "acc_teacher_001",
        "username": "teacher_wang",
        "password_hash": demo_password_hash("acc_teacher_001"),
        "role": "teacher",
        "display_name": "王老师",
        "student_id": None,
        "created_at": "2026-05-01T08:50:00Z",
    },
]

SEED_ACCOUNT_STUDENTS = [
    {"id": "acct_stu_parent_001_001", "account_id": "acc_parent_001", "student_id": "stu_001"},
    {"id": "acct_stu_teacher_001_001", "account_id": "acc_teacher_001", "student_id": "stu_001"},
    {"id": "acct_stu_teacher_001_002", "account_id": "acc_teacher_001", "student_id": "stu_002"},
    {"id": "acct_stu_teacher_001_003", "account_id": "acc_teacher_001", "student_id": "stu_003"},
]

SEED_STUDENT_PROFILES = [
    {
        "id": "profile_stu_001",
        "student_id": "stu_001",
        "weak_points": ["kp_003", "kp_004"],
        "recent_states": ["confused", "frustrated", "frustrated"],
        "effective_strategies": ["small_step", "humor"],
        "learning_summary": "小宇基础尚可，但一遇含参/分类讨论就容易卡，受挫后易说「我不会」放弃。拆小步引导和轻松氛围对他效果好。",
        "total_sessions": 3,
        "updated_at": "2026-05-20T20:00:00Z",
    },
    {
        "id": "profile_stu_002",
        "student_id": "stu_002",
        "weak_points": ["kp_008"],
        "recent_states": ["anxious", "stable", "anxious"],
        "effective_strategies": ["care", "hint"],
        "learning_summary": "小琳基础其实不弱，但极在意分数与考试，一紧张就乱、爱说「来不及了」「会不会考」。需要先安抚情绪、给确定感，再推进；对她不宜用调侃式幽默。",
        "total_sessions": 5,
        "updated_at": "2026-05-21T19:00:00Z",
    },
    {
        "id": "profile_stu_003",
        "student_id": "stu_003",
        "weak_points": [],
        "recent_states": ["stable", "stable", "stable"],
        "effective_strategies": ["socratic"],
        "learning_summary": "小哲基础扎实、肯钻研、情绪稳定，主要问题是偶尔粗心（看错条件、笔误）。适合用追问引导他自查与延展拔高，不需要额外关怀安抚。",
        "total_sessions": 6,
        "updated_at": "2026-05-21T20:00:00Z",
    },
]

SEED_KNOWLEDGE_POINTS = [
    {"id": "kp_001", "name": "函数", "subject": "math", "chapter": "函数", "parent_id": None},
    {"id": "kp_002", "name": "二次函数", "subject": "math", "chapter": "函数", "parent_id": "kp_001"},
    {"id": "kp_003", "name": "二次函数最值", "subject": "math", "chapter": "函数", "parent_id": "kp_002"},
    {"id": "kp_004", "name": "含参讨论", "subject": "math", "chapter": "函数", "parent_id": "kp_002"},
    {"id": "kp_005", "name": "一元二次方程与判别式", "subject": "math", "chapter": "方程", "parent_id": None},
    {"id": "kp_006", "name": "集合运算", "subject": "math", "chapter": "集合", "parent_id": None},
    {"id": "kp_007", "name": "不等式求解", "subject": "math", "chapter": "不等式", "parent_id": None},
    {"id": "kp_008", "name": "立体几何（空间想象）", "subject": "math", "chapter": "立体几何", "parent_id": None},
    {"id": "kp_009", "name": "概率（古典概型）", "subject": "math", "chapter": "概率", "parent_id": None},
]


def make_student_knowledge(
    student_id: str, knowledge_point_id: str, mastery: int, attempts: int, correct_count: int
) -> dict[str, object]:
    """生成学生知识点掌握度种子记录。"""

    return {
        "id": f"sk_{student_id[-3:]}_{knowledge_point_id[-3:]}",
        "student_id": student_id,
        "knowledge_point_id": knowledge_point_id,
        "mastery": mastery,
        "attempts": attempts,
        "correct_count": correct_count,
        "last_practiced_at": "2026-05-21T12:00:00Z",
    }


SEED_STUDENT_KNOWLEDGE = [
    make_student_knowledge("stu_001", "kp_003", 52, 6, 3),
    make_student_knowledge("stu_001", "kp_004", 45, 4, 1),
    make_student_knowledge("stu_001", "kp_002", 70, 8, 6),
    make_student_knowledge("stu_001", "kp_005", 65, 5, 4),
    make_student_knowledge("stu_001", "kp_006", 80, 4, 4),
    make_student_knowledge("stu_002", "kp_008", 48, 5, 2),
    make_student_knowledge("stu_002", "kp_003", 72, 6, 5),
    make_student_knowledge("stu_002", "kp_005", 75, 5, 4),
    make_student_knowledge("stu_002", "kp_006", 82, 4, 4),
    make_student_knowledge("stu_003", "kp_003", 88, 7, 7),
    make_student_knowledge("stu_003", "kp_005", 90, 6, 6),
    make_student_knowledge("stu_003", "kp_006", 85, 5, 5),
    make_student_knowledge("stu_003", "kp_009", 78, 4, 3),
]

SEED_QUESTIONS = [
    {
        "id": "q_001",
        "stem": "已知函数 f(x)=x²−2ax+1，求 f(x) 在区间 [0,2] 上的最小值（用 a 表示）。",
        "standard_answer": "a<0 时最小值 f(0)=1；0≤a≤2 时 f(a)=1−a²；a>2 时 f(2)=5−4a。",
        "solution": "对称轴 x=a。①a<0：f 在[0,2]递增，最小值 f(0)=1。②0≤a≤2：顶点在区间内，最小值 f(a)=1−a²。③a>2：f 递减，最小值 f(2)=5−4a。",
        "difficulty": "hard",
        "typical_errors": [
            {"cause": "concept", "detail": "忽略对称轴位置，直接代端点或顶点，未分类讨论"},
            {"cause": "incomplete", "detail": "只讨论部分情况，漏掉a<0或a>2"},
        ],
        "visual_aid_type": "function_graph",
        "visual_aid_spec": {
            "expr": "x^2-2*a*x+1",
            "param": "a",
            "x_range": [-1, 3],
            "highlight_interval": [0, 2],
            "show_axis_of_symmetry": True,
        },
    },
    {
        "id": "q_002",
        "stem": "求二次函数 f(x)=x²−4x+5 的最小值。",
        "standard_answer": "最小值为 1（在 x=2 处取得）。",
        "solution": "配方 f(x)=(x−2)²+1，顶点 (2,1)，开口向上，最小值 1。",
        "difficulty": "easy",
        "typical_errors": [
            {"cause": "calculation", "detail": "配方时常数项算错"},
            {"cause": "concept", "detail": "误把对称轴x值当成最小值"},
        ],
        "visual_aid_type": "function_graph",
        "visual_aid_spec": {"expr": "x^2-4*x+5", "x_range": [-1, 5], "mark_vertex": True},
    },
    {
        "id": "q_003",
        "stem": "若关于 x 的方程 x²−2x+m=0 有两个不相等的实数根，求 m 的取值范围。",
        "standard_answer": "m<1。",
        "solution": "两个不相等实根需判别式 Δ>0，即 4−4m>0，解得 m<1。",
        "difficulty": "medium",
        "typical_errors": [
            {"cause": "concept", "detail": "混淆Δ>0与Δ≥0"},
            {"cause": "calculation", "detail": "判别式符号或移项出错"},
        ],
        "visual_aid_type": "none",
        "visual_aid_spec": None,
    },
    {
        "id": "q_004",
        "stem": "已知集合 A={x | −1<x≤3}，B={x | x≥2}，求 A∩B。",
        "standard_answer": "A∩B={x | 2≤x≤3}。",
        "solution": "取两集合公共部分，下界取较大者 2（含），上界取较小者 3（含）。",
        "difficulty": "easy",
        "typical_errors": [
            {"cause": "careless", "detail": "端点开闭弄反"},
            {"cause": "misread", "detail": "把交集做成并集"},
        ],
        "visual_aid_type": "diagram",
        "visual_aid_spec": {
            "type": "number_line",
            "sets": [
                {"name": "A", "range": [-1, 3], "open": [True, False]},
                {"name": "B", "range": [2, "inf"], "open": [False, False]},
            ],
        },
    },
    {
        "id": "q_005",
        "stem": "已知函数 f(x)=x²−2ax+1 在区间 [1,3] 上单调递增，求 a 的取值范围。",
        "standard_answer": "a≤1。",
        "solution": "对称轴 x=a，开口向上，在[1,3]递增需对称轴在区间左侧或左端点，即 a≤1。",
        "difficulty": "medium",
        "typical_errors": [
            {"cause": "concept", "detail": "单调性与对称轴位置关系判断错"},
            {"cause": "incomplete", "detail": "漏掉a=1的边界"},
        ],
        "visual_aid_type": "function_graph",
        "visual_aid_spec": {"expr": "x^2-2*a*x+1", "param": "a", "x_range": [0, 4], "highlight_interval": [1, 3]},
    },
    {
        "id": "q_006",
        "stem": "正方体 ABCD-A₁B₁C₁D₁ 的棱长为 2，求异面直线 AC 与 BD₁ 所成角的余弦值。",
        "standard_answer": "余弦值为 √3/3。",
        "solution": "建空间直角坐标系，设各顶点坐标，求向量 AC 与 BD₁ 夹角余弦：数量积除以模长之积，得 √3/3。",
        "difficulty": "hard",
        "typical_errors": [
            {"cause": "concept", "detail": "异面直线所成角与向量夹角取绝对值处理混淆"},
            {"cause": "method", "detail": "不会建系，凭空想象导致卡住"},
        ],
        "visual_aid_type": "geometry",
        "visual_aid_spec": {"type": "cube", "edge": 2, "label_vertices": True, "highlight_lines": ["AC", "BD1"]},
    },
    {
        "id": "q_007",
        "stem": "从 1,2,3,4,5 中任取两个不同的数，求两数之和为偶数的概率。",
        "standard_answer": "2/5。",
        "solution": "总取法 C(5,2)=10；和为偶数需两数同奇偶：奇{1,3,5}取两个 C(3,2)=3，偶{2,4}取两个 C(2,2)=1，共 4 种；概率 4/10=2/5。",
        "difficulty": "medium",
        "typical_errors": [
            {"cause": "careless", "detail": "漏算偶数对或重复计数"},
            {"cause": "concept", "detail": "误用排列A而非组合C"},
        ],
        "visual_aid_type": "none",
        "visual_aid_spec": None,
    },
]

SEED_QUESTION_KNOWLEDGE = [
    {"id": "qk_001_003", "question_id": "q_001", "knowledge_point_id": "kp_003"},
    {"id": "qk_001_004", "question_id": "q_001", "knowledge_point_id": "kp_004"},
    {"id": "qk_002_003", "question_id": "q_002", "knowledge_point_id": "kp_003"},
    {"id": "qk_003_005", "question_id": "q_003", "knowledge_point_id": "kp_005"},
    {"id": "qk_003_007", "question_id": "q_003", "knowledge_point_id": "kp_007"},
    {"id": "qk_004_006", "question_id": "q_004", "knowledge_point_id": "kp_006"},
    {"id": "qk_005_004", "question_id": "q_005", "knowledge_point_id": "kp_004"},
    {"id": "qk_005_003", "question_id": "q_005", "knowledge_point_id": "kp_003"},
    {"id": "qk_006_008", "question_id": "q_006", "knowledge_point_id": "kp_008"},
    {"id": "qk_007_009", "question_id": "q_007", "knowledge_point_id": "kp_009"},
]


def seed_database(connection: Connection | None = None) -> dict[str, int]:
    """向数据库写入完整种子数据，并返回各类数据条数。"""

    owns_connection = connection is None
    db = connection or create_connection()
    for student in SEED_STUDENTS:
        upsert_student(db, Student.model_validate(student))
    for account in SEED_ACCOUNTS:
        upsert_account(db, Account.model_validate(account))
    for relation in SEED_ACCOUNT_STUDENTS:
        upsert_account_student(db, AccountStudent.model_validate(relation))
    for profile in SEED_STUDENT_PROFILES:
        upsert_student_profile(db, StudentProfile.model_validate(profile))
    for point in SEED_KNOWLEDGE_POINTS:
        upsert_knowledge_point(db, KnowledgePoint.model_validate(point))
    for record in SEED_STUDENT_KNOWLEDGE:
        upsert_student_knowledge(db, StudentKnowledge.model_validate(record))
    for question in SEED_QUESTIONS:
        upsert_question(db, Question.model_validate(question))
    for record in SEED_QUESTION_KNOWLEDGE:
        upsert_question_knowledge(db, QuestionKnowledge.model_validate(record))
    db.commit()
    summary = {
        "students": len(SEED_STUDENTS),
        "accounts": len(SEED_ACCOUNTS),
        "account_students": len(SEED_ACCOUNT_STUDENTS),
        "profiles": len(SEED_STUDENT_PROFILES),
        "knowledge_points": len(SEED_KNOWLEDGE_POINTS),
        "student_knowledge": len(SEED_STUDENT_KNOWLEDGE),
        "questions": len(SEED_QUESTIONS),
        "question_knowledge": len(SEED_QUESTION_KNOWLEDGE),
    }
    if owns_connection:
        db.close()
    return summary


def main() -> None:
    """命令行入口：写入默认数据库的种子数据。"""

    summary = seed_database()
    print(f"Seeded database: {summary}")


if __name__ == "__main__":
    main()
