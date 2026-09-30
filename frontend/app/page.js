"use client";
import { useEffect, useRef, useState } from "react";
import ChatPanel from "./components/ChatPanel";
import FilterBar from "./components/FilterBar";
import GraphView from "./components/GraphView";
import NodeDetails from "./components/NodeDetails";
import { fetchFilters, fetchGraph, fetchNode } from "./lib/api";

const EMPTY = { nodes: [], links: [] };
const linkEnd = (end) => (typeof end === "object" ? end.id : end);

export default function Home() {
  const [graphData, setGraphData] = useState(EMPTY);
  const [fullGraphData, setFullGraphData] = useState(EMPTY);
  const [truncated, setTruncated] = useState(false);
  const [filters, setFilters] = useState({ node_types: [], countries: [], categories: [] });
  const [selected, setSelected] = useState({ node_type: "", country: "", category: "" });
  const [selectedNode, setSelectedNode] = useState(null);
  const [neighbors, setNeighbors] = useState([]);
  const graphRef = useRef();

  useEffect(() => {
    fetchFilters().then(setFilters).catch(console.error);
  }, []);

  // Load (or reload on filter change) the graph. setState runs after the await,
  // so this doesn't trigger synchronous cascading renders.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchGraph(selected);
        if (cancelled) return;
        setGraphData({ nodes: data.nodes, links: data.links });
        setTruncated(Boolean(data.truncated));
        setFullGraphData(EMPTY); // leaving focus mode
      } catch (err) {
        console.error("Failed to load graph:", err);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selected]);

  const focusNode = async (node) => {
    setSelectedNode(node);
    try {
      const data = await fetchNode(node.id);
      const nbrs = data.neighbors || [];
      setNeighbors(nbrs);

      const keepIds = new Set(nbrs.map((n) => n.id));
      keepIds.add(node.id);
      const source = fullGraphData.nodes.length > 0 ? fullGraphData : graphData;
      if (fullGraphData.nodes.length === 0) setFullGraphData(graphData);

      setGraphData({
        nodes: source.nodes.filter((n) => keepIds.has(n.id)),
        links: source.links.filter(
          (l) => keepIds.has(linkEnd(l.source)) && keepIds.has(linkEnd(l.target)),
        ),
      });
    } catch (err) {
      console.error("Failed to load neighbors:", err);
    }
  };

  const navigateToNode = (id) => {
    const node = (fullGraphData.nodes.length ? fullGraphData : graphData).nodes.find(
      (n) => n.id === id,
    );
    if (!node) return;
    focusNode(node);
    if (graphRef.current && node.x != null) {
      graphRef.current.centerAt(node.x, node.y, 500);
      graphRef.current.zoom(3, 500);
    }
  };

  const changeFilter = (key, value) => setSelected((s) => ({ ...s, [key]: value }));

  const reset = () => {
    setSelectedNode(null);
    setNeighbors([]);
    if (fullGraphData.nodes.length > 0) {
      setGraphData(fullGraphData);
      setFullGraphData(EMPTY);
    }
    setSelected({ node_type: "", country: "", category: "" });
  };

  const closeDetails = () => {
    setSelectedNode(null);
    setNeighbors([]);
    if (fullGraphData.nodes.length > 0) {
      setGraphData(fullGraphData);
      setFullGraphData(EMPTY);
    }
  };

  return (
    <div className="h-screen bg-slate-950 text-white relative overflow-hidden">
      <FilterBar
        filters={filters}
        selected={selected}
        onChange={changeFilter}
        onReset={reset}
      />
      <GraphView
        graphData={graphData}
        onNodeClick={focusNode}
        selectedNodeId={selectedNode?.id}
        truncated={truncated}
        graphRef={graphRef}
      />
      <NodeDetails
        node={selectedNode}
        neighbors={neighbors}
        onClose={closeDetails}
        onNavigate={navigateToNode}
      />
      <ChatPanel />
    </div>
  );
}
