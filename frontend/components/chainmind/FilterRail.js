"use client";
import { Button } from "@/components/ui/button";
import { LEGEND, isRiskNode, kindFromLabel } from "@/lib/constants";

const HIDDEN = new Set([
  "x", "y", "vx", "vy", "fx", "fy", "index", "__indexColor", "__threeObj",
  "id", "name", "label",
]);

function nodeAttributes(node) {
  return Object.entries(node)
    .filter(([k, v]) => !HIDDEN.has(k) && typeof v !== "object")
    .slice(0, 5);
}

export function FilterRail({ options, values, onChange, onReset, counts, selectedNode, onTrace }) {
  const selectClass = "rail-select";
  return (
    <aside className="evidence-rail hidden w-60 shrink-0 overflow-y-auto border-r border-border md:flex md:flex-col">
      <section className="rail-section">
        <div className="rail-heading">
          <span>Graph filters</span>
          <Button variant="ghost" size="sm" onClick={onReset}>Reset</Button>
        </div>

        <label className="filter-label"><span>Entity type</span></label>
        <select className={selectClass} value={values.node_type} onChange={(e) => onChange("node_type", e.target.value)}>
          <option value="">All types</option>
          {options.node_types.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>

        <label className="filter-label"><span>Country</span></label>
        <select className={selectClass} value={values.country} onChange={(e) => onChange("country", e.target.value)}>
          <option value="">All countries</option>
          {options.countries.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        <label className="filter-label"><span>Category</span></label>
        <select className={selectClass} value={values.category} onChange={(e) => onChange("category", e.target.value)}>
          <option value="">All categories</option>
          {options.categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
      </section>

      <section className="rail-section border-t border-border">
        <h2 className="section-label">Entity register</h2>
        <ul className="mt-3 space-y-2">
          {LEGEND.map(([kind, label]) => (
            <li className="flex items-center gap-2.5 text-xs" key={kind}>
              <span className={`legend-dot bg-${kind}`} />
              <span>{label}</span>
              <span className="ml-auto font-mono text-muted-foreground">{counts[kind] ?? 0}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="rail-section mt-auto border-t border-border">
        <h2 className="section-label">Selected evidence</h2>
        {selectedNode ? (
          <div className="evidence-block mt-3">
            <div className="flex items-center gap-2">
              <span className={`legend-dot bg-${kindFromLabel(selectedNode.label)} node-pulse`} />
              <strong className="truncate text-xs">{selectedNode.name || selectedNode.id}</strong>
            </div>
            <dl className="mt-3 space-y-1.5 text-[11px]">
              <div><dt>Entity</dt><dd>{kindFromLabel(selectedNode.label)}</dd></div>
              {nodeAttributes(selectedNode).map(([k, v]) => (
                <div key={k}><dt>{k}</dt><dd>{String(v)}</dd></div>
              ))}
              {isRiskNode(selectedNode) && (
                <div><dt>Risk</dt><dd className="text-risk">flagged</dd></div>
              )}
            </dl>
            <Button className="mt-3 w-full" size="sm" onClick={() => onTrace(selectedNode)}>
              Trace connections
            </Button>
          </div>
        ) : (
          <p className="mt-3 text-[11px] text-muted-foreground">Select a node to inspect it.</p>
        )}
      </section>
    </aside>
  );
}
