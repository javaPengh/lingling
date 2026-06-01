import type { StudentSummary } from "@shared/api";

interface LearningProps {
  /** 当前登录学生账号对应的学生信息。 */
  student?: StudentSummary | null;
}

/** 学生登录后进入的学习主界面占位。 */
export function Learning({ student }: LearningProps) {
  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_360px]">
      <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
        <div className="border-b border-slate-100 pb-4">
          <h2 className="text-xl font-semibold">{student?.name ?? "学生"}的学习主界面</h2>
          <p className="mt-1 text-sm text-slate-600">
            题目、对话与画图位会在这里汇合。当前身份来自登录账号分流。
          </p>
        </div>
        <div className="mt-5 min-h-72 rounded-md border border-dashed border-slate-300 bg-slate-50" />
      </section>

      <aside className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold">本次复盘</h2>
        <div className="mt-4 min-h-44 rounded-md border border-dashed border-slate-300 bg-slate-50" />
      </aside>
    </div>
  );
}
