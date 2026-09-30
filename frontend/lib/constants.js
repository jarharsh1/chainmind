// Node kinds match the backend labels, lowercased.
export const KINDS = ["supplier", "component", "product", "warehouse", "retailer"];

export const kindFromLabel = (label) => (label || "").toLowerCase();

// Hex approximations of the oklch design tokens, for canvas fills where CSS
// variables can't be used directly.
export const KIND_COLORS = {
  supplier: "#3a9bd6",
  component: "#c99a45",
  product: "#54ac77",
  warehouse: "#6d7f99",
  retailer: "#a86e95",
};
export const RISK_COLOR = "#d55c44";
export const LABEL_COLOR = "#8b98a9";
export const LINK_COLOR = "#3b4757";

// Legend rows (label shown in the rail, backend label used for counting).
export const LEGEND = [
  ["supplier", "Supplier"],
  ["component", "Component"],
  ["product", "Product"],
  ["warehouse", "Warehouse"],
  ["retailer", "Retailer"],
];

// Chat suggestions — each maps to a real question sent to the backend.
export const SUGGESTIONS = [
  { label: "Single-source parts", question: "Which components have only one supplier?" },
  { label: "On-time < 90%", question: "Which suppliers have on-time delivery below 90%?" },
  { label: "Full chain: Galaxy Ultra X", question: "Show the full chain for Galaxy Ultra X from supplier to retailer" },
];

// A node counts as a risk flag when it is a single-sourced component or a
// near-full warehouse.
export function isRiskNode(node) {
  if (!node) return false;
  if (node.alt_supplier_count === 0) return true;
  if (typeof node.utilization_pct === "number" && node.utilization_pct >= 90) return true;
  return false;
}
