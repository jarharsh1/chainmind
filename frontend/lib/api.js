// API client. Base URL is configurable via NEXT_PUBLIC_API_URL so the frontend
// isn't pinned to a hardcoded host.
export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getJSON(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const fetchHealth = () => getJSON("/health");

export const fetchFilters = () => getJSON("/api/filters");

export const fetchNode = (id) => getJSON(`/api/node/${encodeURIComponent(id)}`);

export function fetchGraph({ node_type, country, category } = {}) {
  const params = new URLSearchParams();
  if (node_type) params.append("node_type", node_type);
  if (country) params.append("country", country);
  if (category) params.append("category", category);
  const qs = params.toString();
  return getJSON(qs ? `/api/graph/filtered?${qs}` : "/api/graph");
}

export async function postChat(question) {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body; keep the status-based message
    }
    throw new Error(detail);
  }
  return res.json();
}
