const steps = ["读取记忆", "识别状态", "选择策略", "能力调用", "结构化写回"];

export function Observer() {
  return (
    <section>
      <div className="mb-4">
        <h2 className="text-xl font-semibold">观察面板</h2>
        <p className="mt-1 text-sm text-slate-600">每轮决策链路会按时间线展示。</p>
      </div>
      <div className="grid gap-3 md:grid-cols-5">
        {steps.map((step, index) => (
          <article key={step} className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-semibold text-coral">0{index + 1}</p>
            <h3 className="mt-2 font-semibold">{step}</h3>
            <div className="mt-4 h-20 rounded border border-dashed border-slate-300 bg-slate-50" />
          </article>
        ))}
      </div>
    </section>
  );
}
