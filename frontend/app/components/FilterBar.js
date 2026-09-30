"use client";

// Top bar: brand + node-type / country / category filters + reset.
export default function FilterBar({ filters, selected, onChange, onReset }) {
  const selectClass =
    "p-1.5 bg-slate-900 border border-slate-700 rounded text-xs text-slate-200 " +
    "focus:outline-none focus:border-sky-500";

  return (
    <div className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between gap-2 px-4 py-3 bg-slate-950/80 backdrop-blur border-b border-slate-800">
      <div className="flex items-center gap-3 min-w-0">
        <h1 className="text-lg font-bold text-sky-400 whitespace-nowrap">⛓ ChainMind</h1>
        <span className="text-xs text-slate-500 hidden md:block truncate">
          Supply Chain Intelligence Engine
        </span>
      </div>

      <div className="flex items-center gap-2 flex-wrap justify-end">
        <select
          value={selected.node_type}
          onChange={(e) => onChange("node_type", e.target.value)}
          className={selectClass}
        >
          <option value="">All Types</option>
          {filters.node_types.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>

        <select
          value={selected.country}
          onChange={(e) => onChange("country", e.target.value)}
          className={selectClass}
        >
          <option value="">All Countries</option>
          {filters.countries.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <select
          value={selected.category}
          onChange={(e) => onChange("category", e.target.value)}
          className={selectClass}
        >
          <option value="">All Categories</option>
          {filters.categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <button
          onClick={onReset}
          className="px-2 py-1.5 text-xs text-sky-400 hover:text-sky-300 border border-slate-700 rounded"
        >
          Reset
        </button>
      </div>
    </div>
  );
}
