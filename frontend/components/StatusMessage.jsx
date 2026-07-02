export default function StatusMessage({ tone = "neutral", children }) {
  if (!children) {
    return null;
  }

  const toneClasses = {
    neutral: "border-slate-200 bg-white text-slate-600",
    error: "border-red-200 bg-red-50 text-red-700",
    success: "border-emerald-200 bg-emerald-50 text-emerald-700",
    warning: "border-amber-200 bg-amber-50 text-amber-800",
  };

  return (
    <div
      className={`rounded-xl border px-3 py-2 text-sm ${toneClasses[tone]}`}
      role={tone === "error" ? "alert" : "status"}
    >
      {children}
    </div>
  );
}
