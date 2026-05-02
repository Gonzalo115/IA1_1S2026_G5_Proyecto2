export const API_BASE = "http://3.14.147.186:8000/";

export async function apiFetch(
  path: string,
  options?: RequestInit,
): Promise<Response> {
  return fetch(`${API_BASE}${path}`, options);
}
