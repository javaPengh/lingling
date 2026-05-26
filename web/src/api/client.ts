import type { HealthResponse, StudentsListResponse } from "@shared/api";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBase}${path}`);

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/health");
}

export function getStudents(): Promise<StudentsListResponse> {
  return requestJson<StudentsListResponse>("/students");
}
