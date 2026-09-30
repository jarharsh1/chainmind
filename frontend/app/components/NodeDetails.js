"use client";
import { INTERNAL_NODE_FIELDS, NODE_COLORS } from "../lib/constants";

// Right sidebar: attributes of the selected node + clickable connections.
export default function NodeDetails({ node, neighbors, onClose, onNavigate }) {
  if (!node) return null;
  const color = NODE_COLORS[node.label] || "#666";

  return (
    <div className="absolute top-14 right-0 w-72 h-[calc(100%-56px)] z-20 bg-slate-900/95 backdrop-blur border-l border-slate-700 overflow-y-auto">
      <div className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <span
              className="text-xs px-2 py-0.5 rounded-full"
              style={{ backgroundColor: `${color}33`, color }}
            >
              {node.label}
            </span>
            <h2 className="text-sm font-semibold text-slate-200 mt-2">{node.name}</h2>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white text-sm">✕</button>
        </div>

        <div className="space-y-1 text-xs mb-4">
          {Object.entries(node)
            .filter(([k]) => !INTERNAL_NODE_FIELDS.has(k))
            .map(([key, val]) => (
              <div key={key} className="flex justify-between gap-3 py-1 border-b border-slate-800">
                <span className="text-slate-500">{key}</span>
                <span className="text-slate-300 text-right break-all">{String(val)}</span>
              </div>
            ))}
        </div>

        <h3 className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">
          Connections ({neighbors.length})
        </h3>
        <div className="space-y-1.5">
          {neighbors.map((n, i) => {
            const nColor = NODE_COLORS[n.label] || "#666";
            return (
              <button
                key={`${n.id}-${i}`}
                onClick={() => onNavigate(n.id)}
                className="w-full text-left p-2 bg-slate-800/50 rounded border border-slate-800 hover:border-sky-500 transition text-xs"
              >
                <div className="flex justify-between items-center gap-2">
                  <span className="text-slate-300 truncate">{n.props?.name || n.id}</span>
                  <span
                    className="text-[10px] px-1.5 py-0.5 rounded shrink-0"
                    style={{ backgroundColor: `${nColor}22`, color: nColor }}
                  >
                    {n.label}
                  </span>
                </div>
                <div className="text-slate-600 mt-0.5">
                  {n.direction === "outgoing" ? "→" : "←"} {n.rel_type}
                </div>
              </button>
            );
          })}
          {neighbors.length === 0 && (
            <p className="text-xs text-slate-600">No connections.</p>
          )}
        </div>
      </div>
    </div>
  );
}
