"use client";
import { useEffect, useRef, useState } from "react";
import { Database } from "lucide-react";
import { ChatPanel } from "@/components/chainmind/ChatPanel";
import { FilterRail } from "@/components/chainmind/FilterRail";
import { GraphView } from "@/components/chainmind/GraphView";
import { fetchFilters, fetchGraph, fetchHealth, fetchNode } from "@/lib/api";
import { kindFromLabel } from "@/lib/constants";

const EMPTY = { nodes: [], links: [] };
const linkEnd = (end) => (typeof end === "object" ? end.id : end);

function countByKind(nodes) {
  const counts = {};
  for (const n of nodes) {
    const kind = kindFromLabel(n.label);
    counts[kind] = (counts[kind] || 0) + 1;
  }
  return counts;
}

function deriveEvidence(nodes) {
  const warehouses = nodes.filter((n) => typeof n.utilization_pct === "number");
  if (warehouses.length) {
    const top = warehouses.reduce((a, b) => (b.utilization_pct > a.utilization_pct ? b : a));
    if (top.utilization_pct >= 85) {
      return `${top.name} is operating at ${top.utilization_pct}% capacity.`;
    }
  }
  const single = nodes.find((n) => n.alt_supplier_count === 0);
  return single ? `${single.name} is single-sourced with no alternate supplier.` : null;
}

export default function Home() {
  const [options, setOptions] = useState({ node_types: [], countries: [], categories: [] });
  const [values, setValues] = useState({ node_type: "", country: "", category: "" });
  const [graphData, setGraphData] = useState(EMPTY);
  const [fullGraphData, setFullGraphData] = useState(EMPTY);
  const [truncated, setTruncated] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [neo4j, setNeo4j] = useState("…");
  const graphRef = useRef();

  useEffect(() => {
    fetchFilters().then(setOptions).catch(console.error);
    fetchHealth().then((h) => setNeo4j(h.neo4j)).catch(() => setNeo4j("unavailable"));
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchGraph(values);
        if (cancelled) return;
        setGraphData({ nodes: data.nodes, links: data.links });
        setTruncated(Boolean(data.truncated));
        setFullGraphData(EMPTY);
      } catch (err) {
        console.error("Failed to load graph:", err);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [values]);

  const changeFilter = (key, value) => setValues((v) => ({ ...v, [key]: value }));

  const reset = () => {
    setSelectedNode(null);
    if (fullGraphData.nodes.length) {
      setGraphData(fullGraphData);
      setFullGraphData(EMPTY);
    }
    setValues({ node_type: "", country: "", category: "" });
  };

  const traceNode = async (node) => {
    try {
      const data = await fetchNode(node.id);
      const keep = new Set((data.neighbors || []).map((n) => n.id));
      keep.add(node.id);
      const source = fullGraphData.nodes.length ? fullGraphData : graphData;
      if (!fullGraphData.nodes.length) setFullGraphData(graphData);
      setGraphData({
        nodes: source.nodes.filter((n) => keep.has(n.id)),
        links: source.links.filter(
          (l) => keep.has(linkEnd(l.source)) && keep.has(linkEnd(l.target)),
        ),
      });
      graphRef.current?.zoomToFit(500, 60);
    } catch (err) {
      console.error("Failed to trace node:", err);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="command-bar">
        <div className="brand-mark" aria-hidden="true"><i /><i /><i /></div>
        <strong className="text-sm">ChainMind</strong>
        <span className="hidden font-mono text-[11px] text-muted-foreground sm:inline">
          / supply-chain investigation
        </span>
        <div className="ml-auto flex items-center gap-4 font-mono text-[11px] text-muted-foreground">
          <span className="hidden items-center gap-1.5 md:flex">
            <Database className="size-3.5" />Neo4j · {neo4j}
          </span>
          <span className="operator">OP</span>
        </div>
      </header>

      <div className="workspace-grid">
        <FilterRail
          options={options}
          values={values}
          onChange={changeFilter}
          onReset={reset}
          counts={countByKind(graphData.nodes)}
          selectedNode={selectedNode}
          onTrace={traceNode}
        />
        <GraphView
          graphData={graphData}
          selected={selectedNode}
          onSelect={setSelectedNode}
          truncated={truncated}
          evidence={deriveEvidence(graphData.nodes)}
          graphRef={graphRef}
        />
        <ChatPanel />
      </div>
    </div>
  );
}
