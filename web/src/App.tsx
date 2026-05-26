import { useState } from "react";
import { Learning } from "./pages/Learning";
import { Observer } from "./pages/Observer";
import { Report } from "./pages/Report";
import { StudentPicker } from "./pages/StudentPicker";

type PageKey = "students" | "learning" | "observer" | "report";

const pages: Array<{ key: PageKey; label: string }> = [
  { key: "students", label: "学生" },
  { key: "learning", label: "学习" },
  { key: "observer", label: "观察" },
  { key: "report", label: "报告" }
];

export function App() {
  const [page, setPage] = useState<PageKey>("students");

  return (
    <main className="min-h-screen bg-mist text-ink">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-5">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4">
          <div>
            <p className="text-sm font-medium text-leaf">Lingling V0.1</p>
            <h1 className="text-2xl font-semibold">灵灵老师</h1>
          </div>
          <nav className="flex rounded-md border border-slate-200 bg-white p-1 shadow-sm">
            {pages.map((item) => (
              <button
                key={item.key}
                className={`min-h-10 px-4 text-sm font-medium transition ${
                  page === item.key
                    ? "rounded bg-ink text-white"
                    : "text-slate-600 hover:text-ink"
                }`}
                type="button"
                onClick={() => setPage(item.key)}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </header>

        <section className="flex-1 py-6">
          {page === "students" && <StudentPicker />}
          {page === "learning" && <Learning />}
          {page === "observer" && <Observer />}
          {page === "report" && <Report />}
        </section>
      </div>
    </main>
  );
}
