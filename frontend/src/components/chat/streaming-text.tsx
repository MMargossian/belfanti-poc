import React from "react";

interface StreamingTextProps {
  content: string;
  isStreaming?: boolean;
}

type RenderedNode = string | React.ReactElement;

function renderMarkdown(text: string): RenderedNode[] {
  const result: RenderedNode[] = [];
  const lines = text.split("\n");

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];

    // Code blocks (```...```)
    if (line.startsWith("```")) {
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      result.push(
        <pre
          key={`code-${i}`}
          className="bg-bg-primary/80 border border-border-subtle rounded-md p-3 my-2 overflow-x-auto text-xs font-mono text-text-secondary"
        >
          {codeLines.join("\n")}
        </pre>
      );
      continue;
    }

    // Horizontal rule
    if (/^---+$/.test(line.trim())) {
      result.push(
        <hr key={`hr-${i}`} className="border-border-subtle my-3" />
      );
      i++;
      continue;
    }

    // Table: detect a block of lines starting with |
    if (line.trim().startsWith("|") && line.trim().endsWith("|")) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith("|") && lines[i].trim().endsWith("|")) {
        tableLines.push(lines[i]);
        i++;
      }
      result.push(renderTable(tableLines, i));
      continue;
    }

    // Headings
    if (line.startsWith("### ")) {
      result.push(
        <h3 key={`h3-${i}`} className="text-sm font-semibold text-text-primary mt-3 mb-1">
          {renderInline(line.slice(4), i)}
        </h3>
      );
      i++;
      continue;
    }
    if (line.startsWith("## ")) {
      result.push(
        <h2 key={`h2-${i}`} className="text-base font-bold text-text-primary mt-3 mb-1">
          {renderInline(line.slice(3), i)}
        </h2>
      );
      i++;
      continue;
    }
    if (line.startsWith("# ")) {
      result.push(
        <h1 key={`h1-${i}`} className="text-lg font-bold text-text-primary mt-3 mb-1">
          {renderInline(line.slice(2), i)}
        </h1>
      );
      i++;
      continue;
    }

    // Unordered list items (- or * or •)
    if (/^\s*[-*•]\s+/.test(line)) {
      const listItems: { indent: number; content: string; lineIdx: number }[] = [];
      while (i < lines.length && /^\s*[-*•]\s+/.test(lines[i])) {
        const match = lines[i].match(/^(\s*)/);
        const indent = match ? match[1].length : 0;
        const content = lines[i].replace(/^\s*[-*•]\s+/, "");
        listItems.push({ indent, content, lineIdx: i });
        i++;
      }
      result.push(
        <ul key={`ul-${i}`} className="my-1 space-y-0.5">
          {listItems.map((item) => (
            <li
              key={`li-${item.lineIdx}`}
              className="text-sm text-text-primary flex gap-1.5"
              style={{ paddingLeft: `${Math.max(0, item.indent / 2) * 1}rem` }}
            >
              <span className="text-text-muted mt-0.5">•</span>
              <span>{renderInline(item.content, item.lineIdx)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Ordered list items (1. 2. etc.)
    if (/^\s*\d+\.\s+/.test(line)) {
      const listItems: { num: string; content: string; lineIdx: number }[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        const match = lines[i].match(/^\s*(\d+)\.\s+(.*)/);
        if (match) {
          listItems.push({ num: match[1], content: match[2], lineIdx: i });
        }
        i++;
      }
      result.push(
        <ol key={`ol-${i}`} className="my-1 space-y-0.5">
          {listItems.map((item) => (
            <li
              key={`li-${item.lineIdx}`}
              className="text-sm text-text-primary flex gap-1.5"
            >
              <span className="text-text-muted font-medium min-w-[1.2rem] text-right">{item.num}.</span>
              <span>{renderInline(item.content, item.lineIdx)}</span>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Empty line = paragraph break
    if (line.trim() === "") {
      result.push(<div key={`gap-${i}`} className="h-2" />);
      i++;
      continue;
    }

    // Regular text line
    if (result.length > 0) {
      const lastEl = result[result.length - 1];
      // Only add <br> between consecutive text nodes, not after block elements
      if (typeof lastEl === "string" || (React.isValidElement(lastEl) && lastEl.type === "span")) {
        result.push(<br key={`br-${i}`} />);
      }
    }
    result.push(
      <span key={`line-${i}`}>{renderInline(line, i)}</span>
    );
    i++;
  }

  return result;
}

function renderTable(tableLines: string[], keyBase: number): React.ReactElement {
  const parseRow = (line: string) =>
    line
      .split("|")
      .slice(1, -1)
      .map((cell) => cell.trim());

  // Filter out separator rows (|---|---|)
  const isSeparator = (line: string) => /^\|[\s\-:|]+\|$/.test(line.trim());

  const dataRows = tableLines.filter((l) => !isSeparator(l));
  if (dataRows.length === 0) return <></>;

  const headerCells = parseRow(dataRows[0]);
  const bodyRows = dataRows.slice(1).map(parseRow);

  return (
    <div key={`table-${keyBase}`} className="my-2 border border-border-subtle/50 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-bg-secondary/80">
            {headerCells.map((cell, j) => (
              <th key={j} className="text-left p-2 text-text-muted font-medium text-xs">
                {cell}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bodyRows.map((row, ri) => (
            <tr
              key={ri}
              className={`border-t border-border-subtle/50 ${ri % 2 === 1 ? "bg-bg-secondary/30" : ""}`}
            >
              {row.map((cell, ci) => (
                <td key={ci} className="p-2 text-text-primary text-xs">
                  {renderInline(cell, keyBase + ri)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function renderInline(text: string, lineIdx: number): RenderedNode[] {
  const result: RenderedNode[] = [];
  // Match bold, italic, inline code, links
  const regex = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[([^\]]+)\]\(([^)]+)\))/g;
  let lastIndex = 0;
  let match;
  let partIdx = 0;

  while ((match = regex.exec(text)) !== null) {
    // Push text before match
    if (match.index > lastIndex) {
      result.push(text.slice(lastIndex, match.index));
    }

    if (match[2]) {
      // Bold
      result.push(
        <strong key={`b-${lineIdx}-${partIdx}`}>{match[2]}</strong>
      );
    } else if (match[3]) {
      // Italic
      result.push(<em key={`i-${lineIdx}-${partIdx}`}>{match[3]}</em>);
    } else if (match[4]) {
      // Inline code
      result.push(
        <code
          key={`c-${lineIdx}-${partIdx}`}
          className="bg-bg-hover px-1.5 py-0.5 rounded text-xs font-mono text-accent-blue"
        >
          {match[4]}
        </code>
      );
    } else if (match[5] && match[6]) {
      // Link [text](url)
      result.push(
        <a
          key={`a-${lineIdx}-${partIdx}`}
          href={match[6]}
          className="text-accent-blue underline hover:text-accent-blue/80"
          target="_blank"
          rel="noopener noreferrer"
        >
          {match[5]}
        </a>
      );
    }

    lastIndex = match.index + match[0].length;
    partIdx++;
  }

  // Push remaining text
  if (lastIndex < text.length) {
    result.push(text.slice(lastIndex));
  }

  return result;
}

export function StreamingText({ content, isStreaming = false }: StreamingTextProps) {
  if (!content) return null;

  const rendered = renderMarkdown(content);

  return (
    <div className={`text-sm leading-relaxed text-text-primary ${isStreaming ? "streaming-cursor" : ""}`}>
      {rendered}
    </div>
  );
}
