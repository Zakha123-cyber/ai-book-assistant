export default function StatusMessage({ tone = "neutral", children }) {
  if (!children) {
    return null;
  }

  const toneClasses = {
    neutral: "border-neutral-800 bg-neutral-900 text-neutral-300",
    error: "border-red-900/70 bg-red-950/70 text-red-200",
    success: "border-emerald-900/70 bg-emerald-950/70 text-emerald-200",
    warning: "border-amber-900/70 bg-amber-950/70 text-amber-200",
  };

  return (
    <div
      className={`rounded-md border px-3 py-2 text-sm ${toneClasses[tone]}`}
      role={tone === "error" ? "alert" : "status"}
    >
      {children}
    </div>
  );
}
