"use client";
import { useEffect, useRef, useState } from "react";
import { Check, ChevronDown, Copy, Send, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { postChat } from "@/lib/api";
import { SUGGESTIONS } from "@/lib/constants";

function rowLabel(row) {
  const vals = Object.values(row).map((v) => String(v));
  return { main: vals[0] ?? "", meta: vals.slice(1).join(" · ") };
}

function CypherBlock({ cypher }) {
  const [copied, setCopied] = useState(false);
  if (!cypher || cypher === "N/A") return null;
  return (
    <details className="cypher-block" open>
      <summary>
        <span>Generated Cypher</span>
        <ChevronDown />
        <span className="ml-auto flex items-center gap-1 text-product">read-only <Check /></span>
      </summary>
      <pre><code>{cypher}</code></pre>
      <Button
        variant="ghost"
        size="icon"
        className="copy-button"
        aria-label="Copy Cypher"
        onClick={() => {
          navigator.clipboard?.writeText(cypher);
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        }}
      >
        {copied ? <Check /> : <Copy />}
      </Button>
    </details>
  );
}

export function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [turns]);

  const run = async (text) => {
    const q = (text ?? question).trim();
    if (!q) return;
    setQuestion("");
    const idx = turns.length;
    setTurns((t) => [...t, { question: q, status: "loading" }]);
    try {
      const data = await postChat(q);
      setTurns((t) => t.map((turn, i) => (i === idx ? { ...turn, status: "done", ...data } : turn)));
    } catch (err) {
      setTurns((t) => t.map((turn, i) => (i === idx ? { ...turn, status: "error", error: err.message } : turn)));
    }
  };

  return (
    <aside className="investigation-rail flex min-h-[560px] w-full shrink-0 flex-col border-l border-border xl:w-[390px]">
      <header className="flex h-12 items-center gap-2 border-b border-border px-4">
        <strong className="text-xs">Investigation dossier</strong>
        <span className="font-mono text-[10px] text-muted-foreground">CM–0926</span>
        <span className="ml-auto flex items-center gap-1 font-mono text-[10px] text-product">
          <ShieldCheck /> guarded
        </span>
      </header>

      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
        {turns.length === 0 && (
          <p className="text-[13px] text-muted-foreground">
            Ask the supply graph to open an investigation. Every query is generated read-only and guarded before it runs.
          </p>
        )}

        {turns.map((turn, i) => (
          <div key={i} className="space-y-3">
            <div className="flex justify-end">
              <p className="max-w-[88%] rounded-md rounded-tr-sm border border-border bg-raised px-3 py-2 text-[13px]">
                {turn.question}
              </p>
            </div>

            {turn.status === "loading" && (
              <p className="animate-pulse font-mono text-[11px] text-muted-foreground">Querying graph…</p>
            )}

            {turn.status === "error" && (
              <section className="evidence-block border-l-2 border-l-risk">
                <span className="section-label text-risk">Error</span>
                <p className="mt-1 text-[13px]">{turn.error}</p>
              </section>
            )}

            {turn.status === "done" && (
              <>
                <section className="evidence-block border-l-2 border-l-supplier">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="section-label">Finding</span>
                    <span className="ml-auto font-mono text-[10px] text-muted-foreground">
                      {turn.results?.length ?? 0} rows · {turn.category}
                    </span>
                  </div>
                  <p className="whitespace-pre-wrap text-[13px] leading-relaxed">{turn.answer}</p>
                </section>

                <CypherBlock cypher={turn.cypher} />

                {turn.results?.length > 0 && (
                  <section className="border-t border-border pt-3">
                    <h2 className="section-label">Evidence stack</h2>
                    <div className="mt-2 grid gap-2">
                      {turn.results.slice(0, 4).map((row, r) => {
                        const { main, meta } = rowLabel(row);
                        return (
                          <div className="mini-evidence" key={r}>
                            <b>{String(r + 1).padStart(2, "0")}</b>
                            <span>{main}</span>
                            <em>{meta}</em>
                          </div>
                        );
                      })}
                    </div>
                  </section>
                )}
              </>
            )}
          </div>
        ))}
      </div>

      <footer className="border-t border-border p-4">
        <div className="mb-3 flex flex-wrap gap-1.5">
          {SUGGESTIONS.map((s) => (
            <Button key={s.label} variant="outline" size="sm" onClick={() => run(s.question)}>
              {s.label}
            </Button>
          ))}
        </div>
        <div className="flex items-end gap-2 rounded-md border border-border bg-raised p-2 focus-within:border-supplier">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                run();
              }
            }}
            rows={1}
            className="min-h-8 flex-1 resize-none bg-transparent px-1 text-[13px] outline-none placeholder:text-muted-foreground"
            placeholder="Ask the supply graph…"
          />
          <Button size="icon" aria-label="Run investigation" onClick={() => run()}>
            <Send />
          </Button>
        </div>
      </footer>
    </aside>
  );
}
