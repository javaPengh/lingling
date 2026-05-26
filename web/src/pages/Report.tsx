export function Report() {
  return (
    <section>
      <div className="mb-4">
        <h2 className="text-xl font-semibold">报告预览</h2>
        <p className="mt-1 text-sm text-slate-600">教师视角与家长视角摘要会并排展示。</p>
      </div>
      <div className="grid gap-5 md:grid-cols-2">
        {["教师视角", "家长视角"].map((title) => (
          <article key={title} className="rounded-md border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="font-semibold">{title}</h3>
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
