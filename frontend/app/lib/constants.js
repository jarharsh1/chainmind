// Shared design tokens for the graph node types.
export const NODE_COLORS = {
  Supplier: "#a78bfa",
  Component: "#fb923c",
  Product: "#38bdf8",
  Warehouse: "#4ade80",
  Retailer: "#f472b6",
};

// Fields that are internal to the force-graph engine, hidden in node details.
export const INTERNAL_NODE_FIELDS = new Set([
  "x", "y", "vx", "vy", "fx", "fy", "index", "__indexColor", "label", "name",
]);

export const SAMPLE_QUESTIONS = [
  "Which components have only one supplier?",
  "If Taiwan Semiconductor Co goes down, which products are affected?",
  "What is the cheapest route to Flipkart India?",
  "Which warehouse is closest to full capacity?",
];
