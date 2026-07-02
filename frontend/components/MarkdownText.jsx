function parseMarkdown(text) {
  const blocks = [];
  let paragraph = [];
  let list = null;

  function flushParagraph() {
    if (!paragraph.length) {
      return;
    }
    blocks.push({
      type: "paragraph",
      text: paragraph.join(" "),
    });
    paragraph = [];
  }

  function flushList() {
    if (!list) {
      return;
    }
    blocks.push(list);
    list = null;
  }

  for (const rawLine of String(text || "").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) {
      flushParagraph();
      flushList();
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      blocks.push({
        type: "heading",
        level: heading[1].length,
        text: heading[2].trim(),
      });
      continue;
    }

    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (bullet) {
      flushParagraph();
      if (!list || list.type !== "bulletList") {
        flushList();
        list = { type: "bulletList", items: [] };
      }
      list.items.push(bullet[1].trim());
      continue;
    }

    const ordered = line.match(/^\d+[.)]\s+(.+)$/);
    if (ordered) {
      flushParagraph();
      if (!list || list.type !== "orderedList") {
        flushList();
        list = { type: "orderedList", items: [] };
      }
      list.items.push(ordered[1].trim());
      continue;
    }

    flushList();
    paragraph.push(line);
  }

  flushParagraph();
  flushList();
  return blocks;
}

function renderInline(text) {
  return String(text)
    .split(/(\*\*[^*]+\*\*)/g)
    .filter(Boolean)
    .map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong className="font-semibold text-slate-900" key={index}>
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <span key={index}>{part}</span>;
    });
}

export default function MarkdownText({ text, className = "" }) {
  const blocks = parseMarkdown(text);

  return (
    <div className={`space-y-3 text-sm leading-6 text-slate-700 ${className}`}>
      {blocks.map((block, index) => {
        if (block.type === "heading") {
          const headingClass =
            block.level <= 1
              ? "text-lg font-semibold text-slate-900"
              : "text-base font-semibold text-slate-900";
          return (
            <h3 className={headingClass} key={index}>
              {renderInline(block.text)}
            </h3>
          );
        }

        if (block.type === "bulletList") {
          return (
            <ul className="list-disc space-y-2 pl-5" key={index}>
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>{renderInline(item)}</li>
              ))}
            </ul>
          );
        }

        if (block.type === "orderedList") {
          return (
            <ol className="list-decimal space-y-2 pl-5" key={index}>
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>{renderInline(item)}</li>
              ))}
            </ol>
          );
        }

        return <p key={index}>{renderInline(block.text)}</p>;
      })}
    </div>
  );
}
