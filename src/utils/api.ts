export const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
// if (!import.meta.env.VITE_API_BASE_URL) console.warn('VITE_API_BASE_URL is not defined, defaulting to http://localhost:5000');

const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '');
const ensureLeadingSlash = (value: string) => (value.startsWith('/') ? value : `/${value}`);

const extractErrorMessage = (payload: unknown, fallback: string) => {
  if (!payload) return fallback;

  if (typeof payload === 'string') {
    return payload.trim() || fallback;
  }

  if (typeof payload === 'object') {
    const messageLike =
      // @ts-expect-error index signature not declared on purpose
      payload?.message ?? payload?.detail ?? payload?.error ?? payload?.errors;
    if (Array.isArray(messageLike)) {
      return messageLike.map(item => (typeof item === 'string' ? item : '')).join('\n') || fallback;
    }
    if (messageLike) {
      return String(messageLike);
    }
  }

  return fallback;
};

export async function apiFetch<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const base = API_BASE ? trimTrailingSlash(API_BASE) : '';

  const url = `${base}${ensureLeadingSlash(path)}`;
  const token = localStorage.getItem('auth_token');
  const headers: HeadersInit = {
    ...(init?.headers || {}),
  };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  if (!('Content-Type' in (headers as Record<string, string>)) && init?.body) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  const response = await fetch(url, { ...init, headers });

  const contentType = response.headers.get('content-type') ?? '';
  const expectsJson = contentType.includes('application/json');

  let payload: unknown = undefined;
  if (response.status !== 204) {
    try {
      if (expectsJson) {
        payload = await response.json();
      } else {
        const text = await response.text();
        payload = text ? text : undefined;
      }
    } catch (error) {
      console.error('Failed to parse API response', error);
    }
  }

  if (!response.ok) {
    const fallbackMessage = `HTTP ${response.status} ${response.statusText}`;
    throw new Error(extractErrorMessage(payload, fallbackMessage));
  }

  return (payload as T) ?? (undefined as T);
}
