export const API_BASE = import.meta.env.VITE_API_BASE_URL;
if (!API_BASE) console.error("VITE_API_BASE_URL is not defined");

export async function apiFetch<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  if (!API_BASE) {
    console.error("Cannot perform request without API base URL");
    throw new Error("API base URL is not defined");
  }

  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}
