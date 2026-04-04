"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import dynamic from "next/dynamic";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

const API = "https://chainmind-production.up.railway.app";

const NODE_COLORS = {
  Supplier: "#a78bfa",
  Component: "#fb923c",
  Product: "#38bdf8",
  Warehouse: "#4ade80",
  Retailer: "#f472b6",
};

export default function Home() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [filters, setFilters] = useState({ node_types: [], countries: [], categories: [] });
  const [selectedType, setSelectedType] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedNode, setSelectedNode] = useState(null);
  const [neighbors, setNeighbors] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const graphRef = useRef();

  const loadGraph = useCallback(async () => {
    try {
      let url = `${API}/api/graph`;
      const params = new URLSearchParams();
      if (selectedType) params.append("node_type", selectedType);
      if (selectedCountry) params.append("country", selectedCountry);
      if (selectedCategory) params.append("category", selectedCategory);
      if (params.toString()) url = `${API}/api/graph/filtered?${params.toString()}`;
      const res = await fetch(url);
      const data = await res.json();
      setGraphData(data);
    } catch (err) {
      console.error("Failed to load graph:", err);
    }
  }, [selectedType, selectedCountry, selectedCategory]);

  useEffect(() => {
    fetch(`${API}/api/filters`).then((r) => r.json()).then(setFilters).catch(console.error);
  }, []);

  useEffect(() => { loadGraph(); }, [loadGraph]);

  const [fullGraphData, setFullGraphData] = useState({ nodes: [], links: [] });

  const handleNodeClick = async (node) => {
    setSelectedNode(node);
    setSidebarOpen(true);
    try {
      const res = await fetch(`${API}/api/node/${node.id}`);
      const data = await res.json();
      setNeighbors(data.neighbors || []);

      // Filter graph — show only clicked node + its neighbors
      const neighborIds = new Set((data.neighbors || []).map((n) => n.id));
      neighborIds.add(node.id);

      const source = fullGraphData.nodes.length > 0 ? fullGraphData : graphData;

      const filteredNodes = source.nodes.filter((n) => neighborIds.has(n.id));
      const filteredLinks = source.links.filter(
        (l) => neighborIds.has(typeof l.source === "object" ? l.source.id : l.source) &&
               neighborIds.has(typeof l.target === "object" ? l.target.id : l.target)
      );

      if (fullGraphData.nodes.length === 0) {
        setFullGraphData(graphData);
      }

      setGraphData({ nodes: filteredNodes, links: filteredLinks });
    } catch (err) {
      console.error("Failed to load neighbors:", err);
    }
  };

  const navigateToNode = (neighborId) => {
    const node = graphData.nodes.find((n) => n.id === neighborId);
    if (node) {
      handleNodeClick(node);
      if (graphRef.current) {
        graphRef.current.centerAt(node.x, node.y, 500);
        graphRef.current.zoom(3, 500);
      }
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const question = chatInput;
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", text: question }]);
    setChatLoading(true);
    try {
      const res = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setChatMessages((prev) => [...prev, { role: "assistant", text: data.answer, cypher: data.cypher, category: data.category }]);
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: "assistant", text: "Error: Could not reach the API." }]);
    }
    setChatLoading(false);
  };

 const resetFilters = () => {
    setSelectedType("");
    setSelectedCountry("");
    setSelectedCategory("");
    setSelectedNode(null);
    setNeighbors([]);
    if (fullGraphData.nodes.length > 0) {
      setGraphData(fullGraphData);
      setFullGraphData({ nodes: [], links: [] });
    }
  };

  return (
    <div className="h-screen bg-gray-950 text-white relative overflow-hidden">

      {/* TOP BAR */}
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-3 bg-gray-950/80 backdrop-blur border-b border-gray-800">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-bold text-blue-400">⛓ ChainMind</h1>
          <span className="text-xs text-gray-500 hidden sm:block">Supply Chain Intelligence Engine</span>
        </div>
        <div className="flex items-center gap-2">
          <select value={selectedType} onChange={(e) => setSelectedType(e.target.value)} className="p-1.5 bg-gray-900 border border-gray-700 rounded text-xs">
            <option value="">All Types</option>
            {filters.node_types.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={selectedCountry} onChange={(e) => setSelectedCountry(e.target.value)} className="p-1.5 bg-gray-900 border border-gray-700 rounded text-xs">
            <option value="">All Countries</option>
            {filters.countries.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="p-1.5 bg-gray-900 border border-gray-700 rounded text-xs">
            <option value="">All Categories</option>
            {filters.categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <button onClick={resetFilters} className="px-2 py-1.5 text-xs text-blue-400 hover:text-blue-300 border border-gray-700 rounded">Reset</button>
        </div>
      </div>

      {/* LEGEND — bottom left */}
      <div className="absolute bottom-4 left-4 z-10 bg-gray-900/90 backdrop-blur border border-gray-700 rounded-lg p-3">
        <div className="grid grid-cols-5 gap-3">
          {Object.entries(NODE_COLORS).map(([label, color]) => (
            <div key={label} className="flex items-center gap-1.5 text-xs">
              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-gray-400">{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* GRAPH — full screen */}
      <div className="absolute inset-0 pt-14">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeId="id"
          nodeLabel="name"
          nodeColor={(node) => NODE_COLORS[node.label] || "#666"}
          nodeRelSize={6}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkColor={() => "#334155"}
          linkLabel={(link) => link.type}
          onNodeClick={handleNodeClick}
          backgroundColor="#030712"
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name || node.id;
            const fontSize = Math.max(10 / globalScale, 2);
            const size = 6;
            const isSelected = selectedNode && selectedNode.id === node.id;

            if (isSelected) {
              ctx.beginPath();
              ctx.arc(node.x, node.y, size + 3, 0, 2 * Math.PI);
              ctx.fillStyle = "rgba(59, 130, 246, 0.3)";
              ctx.fill();
            }

            ctx.beginPath();
            ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
            ctx.fillStyle = NODE_COLORS[node.label] || "#666";
            ctx.fill();

            if (globalScale > 0.8) {
              ctx.font = `${fontSize}px Sans-Serif`;
              ctx.textAlign = "center";
              ctx.textBaseline = "top";
              ctx.fillStyle = "#e2e8f0";
              const shortLabel = label.length > 18 ? label.slice(0, 16) + ".." : label;
              ctx.fillText(shortLabel, node.x, node.y + size + 2);
            }
          }}
          nodePointerAreaPaint={(node, color, ctx) => {
            ctx.beginPath();
            ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
          }}
        />
      </div>

      {/* NODE DETAILS — right sidebar */}
      {selectedNode && sidebarOpen && (
        <div className="absolute top-14 right-0 w-72 h-[calc(100%-56px)] z-10 bg-gray-900/95 backdrop-blur border-l border-gray-700 overflow-y-auto">
          <div className="p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: NODE_COLORS[selectedNode.label] + "33", color: NODE_COLORS[selectedNode.label] }}>
                  {selectedNode.label}
                </span>
                <h2 className="text-sm font-semibold text-gray-200 mt-2">{selectedNode.name}</h2>
              </div>
              <button onClick={() => { setSidebarOpen(false); setSelectedNode(null); resetFilters(); }} className="text-gray-500 hover:text-white text-sm">✕</button>
            </div>

            <div className="space-y-1 text-xs text-gray-400 mb-4">
              {Object.entries(selectedNode)
                .filter(([k]) => !["x", "y", "vx", "vy", "fx", "fy", "index", "__indexColor", "label", "name"].includes(k))
                .map(([key, val]) => (
                  <div key={key} className="flex justify-between py-1 border-b border-gray-800">
                    <span className="text-gray-500">{key}</span>
                    <span className="text-gray-300">{String(val)}</span>
                  </div>
                ))}
            </div>

            <h3 className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">
              Connections ({neighbors.length})
            </h3>
            <div className="space-y-1.5">
              {neighbors.map((n, i) => (
                <button
                  key={i}
                  onClick={() => navigateToNode(n.id)}
                  className="w-full text-left p-2 bg-gray-800/50 rounded border border-gray-800 hover:border-blue-500 transition text-xs"
                >
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300">{n.props?.name || n.id}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ backgroundColor: NODE_COLORS[n.label] + "22", color: NODE_COLORS[n.label] }}>
                      {n.label}
                    </span>
                  </div>
                  <div className="text-gray-600 mt-0.5">
                    {n.direction === "outgoing" ? "→" : "←"} {n.rel_type}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* FLOATING CHATBOT */}
      <div className="fixed bottom-4 right-4 z-50">
        {!chatOpen ? (
          <button onClick={() => setChatOpen(true)} className="w-14 h-14 bg-blue-600 rounded-full flex items-center justify-center shadow-lg hover:bg-blue-500 transition text-xl">
            💬
          </button>
        ) : (
          <div className="w-96 h-[500px] bg-gray-900 border border-gray-700 rounded-xl shadow-2xl flex flex-col">
            <div className="p-3 border-b border-gray-700 flex justify-between items-center">
              <div>
                <h2 className="text-sm font-semibold text-gray-200">GraphRAG Chat</h2>
                <p className="text-xs text-gray-500">Ask about your supply chain</p>
              </div>
              <button onClick={() => setChatOpen(false)} className="text-gray-500 hover:text-white text-lg">✕</button>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              {chatMessages.length === 0 && (
                <div className="text-xs text-gray-600 space-y-2">
                  <p>Try asking:</p>
                  <button onClick={() => setChatInput("Which components have only one supplier?")} className="block w-full text-left p-2 bg-gray-800 rounded border border-gray-700 hover:border-blue-500 transition">
                    Which components have only one supplier?
                  </button>
                  <button onClick={() => setChatInput("If Taiwan Semiconductor goes down, which products are affected?")} className="block w-full text-left p-2 bg-gray-800 rounded border border-gray-700 hover:border-blue-500 transition">
                    If Taiwan Semiconductor goes down?
                  </button>
                  <button onClick={() => setChatInput("What is the cheapest route to Flipkart India?")} className="block w-full text-left p-2 bg-gray-800 rounded border border-gray-700 hover:border-blue-500 transition">
                    Cheapest route to Flipkart India?
                  </button>
                </div>
              )}

              {chatMessages.map((msg, i) => (
                <div key={i} className={`text-sm p-3 rounded-lg ${msg.role === "user" ? "bg-blue-900/30 border border-blue-800 ml-6" : "bg-gray-800 border border-gray-700 mr-4"}`}>
                  <p className="text-gray-200 whitespace-pre-wrap">{msg.text}</p>
                  {msg.cypher && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">View Cypher</summary>
                      <pre className="mt-1 text-xs text-green-400 bg-gray-950 p-2 rounded overflow-x-auto">{msg.cypher}</pre>
                    </details>
                  )}
                </div>
              ))}

              {chatLoading && <div className="text-xs text-gray-500 animate-pulse p-3">Querying graph...</div>}
            </div>

            <div className="p-3 border-t border-gray-700">
              <form onSubmit={handleChat} className="flex gap-2">
                <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Ask something..." className="flex-1 p-2 bg-gray-800 border border-gray-700 rounded text-sm focus:outline-none focus:border-blue-500" />
                <button type="submit" disabled={chatLoading} className="px-3 py-2 bg-blue-600 rounded text-sm hover:bg-blue-500 disabled:opacity-50">➤</button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}