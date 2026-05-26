import { useEffect, useState } from "react";
import type { StudentSummary } from "@shared/api";
import { getStudents } from "../api/client";

export function StudentPicker() {
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    getStudents()
      .then((data) => {
        setStudents(data.students);
        setStatus("ready");
      })
      .catch(() => {
        setStatus("error");
      });
  }, []);

  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
      <section>
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">学生选择</h2>
            <p className="mt-1 text-sm text-slate-600">选择一个预置画像进入学习主界面。</p>
          </div>
          <span className="rounded bg-white px-3 py-1 text-sm text-slate-600 shadow-sm">
            {status === "loading" ? "连接中" : status === "error" ? "未连接" : `${students.length} 人`}
          </span>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {students.map((student) => (
            <button
              key={student.id}
              className="rounded-md border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-leaf hover:shadow"
              type="button"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded bg-leaf text-lg font-semibold text-white">
                {student.name.slice(0, 1)}
              </div>
              <h3 className="font-semibold">{student.name}</h3>
              <p className="mt-1 text-sm text-slate-600">{student.grade}</p>
              {student.profileLabel && (
                <p className="mt-3 inline-flex rounded bg-mist px-2 py-1 text-xs text-slate-600">
                  {student.profileLabel}
                </p>
              )}
            </button>
          ))}
        </div>

        {status === "ready" && students.length === 0 && (
          <div className="rounded-md border border-dashed border-slate-300 bg-white p-6 text-sm text-slate-600">
            数据库种子数据接入后，这里会显示小宇、小琳、小哲。
          </div>
        )}
      </section>

      <aside className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold">今日入口</h2>
        <div className="mt-4 space-y-3 text-sm text-slate-600">
          <p>当前骨架已连接后端学生列表接口。</p>
          <p>下一步会由 seed 脚本写入三位演示学生。</p>
        </div>
      </aside>
    </div>
  );
}
