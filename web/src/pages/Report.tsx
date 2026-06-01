import type { StudentSummary } from "@shared/api";

interface ReportProps {
  /** 当前报告视角，家长只看关联孩子，老师看所带学生。 */
  role?: "parent" | "teacher";

  /** 当前登录账号可查看的学生列表。 */
  students?: StudentSummary[];
}

/** 家长或老师登录后进入的报告视角占位。 */
export function Report({ role = "teacher", students = [] }: ReportProps) {
  const isTeacher = role === "teacher";
  const title = isTeacher ? "老师报告视角" : "家长报告视角";
  const description = isTeacher
    ? "查看所带学生的学习情况、薄弱点与干预记录。"
    : "查看孩子的学习摘要、状态与陪伴建议。";

  return (
    <section>
      <div className="mb-4">
        <h2 className="text-xl font-semibold">{title}</h2>
        <p className="mt-1 text-sm text-slate-600">{description}</p>
      </div>

      <div className="mb-5 rounded-md border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="font-semibold">可查看学生</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {students.map((student) => (
            <span key={student.id} className="rounded-full bg-[#fbf6ef] px-3 py-1 text-sm text-[#7c7064]">
              {student.name} · {student.grade}
            </span>
          ))}
          {students.length === 0 && <span className="text-sm text-slate-500">暂无关联学生</span>}
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {(isTeacher ? ["班级摘要", "干预建议"] : ["学习摘要", "陪伴建议"]).map((cardTitle) => (
          <article key={cardTitle} className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="font-semibold">{cardTitle}</h3>
            <div className="mt-5 space-y-3">
              <div className="h-4 rounded bg-slate-100" />
              <div className="h-4 w-5/6 rounded bg-slate-100" />
              <div className="h-4 w-2/3 rounded bg-slate-100" />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
