"use client";
import { useState } from "react";

// Shows the generated Cypher for an answer — collapsible, with copy-to-clipboard.
export default function CypherBadge({ cypher }) {
  const [copied, setCopied] = useState(false);
  if (!cypher || cypher === "N/A") return null;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(cypher);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard blocked; ignore
    }
  };

  return (
    <details className="mt-2 group">
      <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-300 select-none">
        View Cypher
      </summary>
      <div className="relative mt-1">
        <button
          onClick={copy}
          className="absolute top-1 right-1 text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 hover:bg-slate-700"
        >
          {copied ? "Copied" : "Copy"}
        </button>
        <pre className="text-xs text-emerald-400 bg-slate-950 p-2 pr-14 rounded overflow-x-auto whitespace-pre-wrap break-words">
          {cypher}
        </pre>
      </div>
    </details>
  );
}
