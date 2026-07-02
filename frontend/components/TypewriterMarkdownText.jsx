"use client";

import { useEffect, useMemo, useState } from "react";

import MarkdownText from "./MarkdownText";

export default function TypewriterMarkdownText({
  text,
  className = "",
  enabled = true,
  onDone,
}) {
  const chunks = useMemo(
    () => String(text || "").match(/\S+\s*/g) || [],
    [text],
  );
  const [visibleCount, setVisibleCount] = useState(0);
  const visibleText = enabled
    ? chunks.slice(0, visibleCount).join("")
    : String(text || "");

  useEffect(() => {
    if (!enabled || chunks.length === 0) {
      const timeoutId = window.setTimeout(() => onDone?.(), 0);
      return () => window.clearTimeout(timeoutId);
    }

    const intervalId = window.setInterval(() => {
      setVisibleCount((current) => {
        const next = Math.min(current + 1, chunks.length);
        if (next >= chunks.length) {
          window.clearInterval(intervalId);
          window.setTimeout(() => onDone?.(), 0);
        }
        return next;
      });
    }, 28);

    return () => window.clearInterval(intervalId);
  }, [chunks.length, enabled, onDone]);

  return (
    <div className="relative">
      <MarkdownText className={className} text={visibleText} />
      {enabled && visibleCount < chunks.length ? (
        <span className="ml-1 inline-block h-4 w-1 animate-pulse rounded-full bg-[#4F6F52] align-middle" />
      ) : null}
    </div>
  );
}
