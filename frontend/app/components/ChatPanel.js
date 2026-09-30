"use client";
import { useEffect, useRef, useState } from "react";
import { postChat } from "../lib/api";
import { SAMPLE_QUESTIONS } from "../lib/constants";
import CypherBadge from "./CypherBadge";

// Self-contained floating GraphRAG chat with loading / empty / error states.
export default function ChatPanel() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, loading]);

  const send = async (e) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setLoading(true);
    try {
      const data = await postChat(question);
      setMessages((m) => [
        ...m,
        { role: "assistant", text: data.answer, cypher: data.cypher, category: data.category },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", error: true, text: `Couldn't reach the API: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-4 right-4 z-50 w-14 h-14 bg-sky-600 rounded-full flex items-center justify-center shadow-lg hover:bg-sky-500 transition text-xl"
        aria-label="Open chat"
      >
        💬
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-[92vw] max-w-96 h-[70vh] max-h-[500px] bg-slate-900 border border-slate-700 rounded-xl shadow-2xl flex flex-col">
      <div className="p-3 border-b border-slate-700 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">GraphRAG Chat</h2>
          <p className="text-xs text-slate-500">Ask about your supply chain</p>
        </div>
        <button onClick={() => setOpen(false)} className="text-slate-500 hover:text-white text-lg" aria-label="Close chat">✕</button>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 && !loading && (
          <div className="text-xs text-slate-500 space-y-2">
            <p>Try asking:</p>
            {SAMPLE_QUESTIONS.map((q) => (
              <button
                key={q}
                onClick={() => setInput(q)}
                className="block w-full text-left p-2 bg-slate-800 rounded border border-slate-700 hover:border-sky-500 transition text-slate-300"
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`text-sm p-3 rounded-lg ${
              msg.role === "user"
                ? "bg-sky-900/30 border border-sky-800 ml-6"
                : msg.error
                  ? "bg-red-950/40 border border-red-800 mr-4"
                  : "bg-slate-800 border border-slate-700 mr-4"
            }`}
          >
            <p className={`whitespace-pre-wrap ${msg.error ? "text-red-300" : "text-slate-200"}`}>
              {msg.text}
            </p>
            {msg.role === "assistant" && !msg.error && <CypherBadge cypher={msg.cypher} />}
          </div>
        ))}

        {loading && (
          <div className="text-xs text-slate-500 animate-pulse p-3">Querying graph...</div>
        )}
      </div>

      <div className="p-3 border-t border-slate-700">
        <form onSubmit={send} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something..."
            className="flex-1 p-2 bg-slate-800 border border-slate-700 rounded text-sm text-slate-100 focus:outline-none focus:border-sky-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-3 py-2 bg-sky-600 rounded text-sm hover:bg-sky-500 disabled:opacity-50"
          >
            ➤
          </button>
        </form>
      </div>
    </div>
  );
}
