const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function get(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status}`);
  }
  return res.json();
}

async function post(path) {
  const res = await fetch(`${BASE_URL}${path}`, { method: "POST" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${path} failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  dashboard: () => get("/api/dashboard"),
  daily: (days) => get(`/api/analytics/daily${days ? `?days=${days}` : ""}`),
  monthly: () => get("/api/analytics/monthly"),
  yearly: () => get("/api/analytics/yearly"),
  platforms: () => get("/api/analytics/platforms"),
  difficulty: () => get("/api/analytics/difficulty"),
  heatmap: () => get("/api/analytics/heatmap"),
  ratingHistory: (platform) =>
    get(`/api/analytics/rating-history${platform ? `?platform=${platform}` : ""}`),
  syncCodeforces: () => post("/api/sync/codeforces"),
  syncLeetcode: () => post("/api/sync/leetcode"),
};
