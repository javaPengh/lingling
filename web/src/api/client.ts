import type { HealthResponse, LoginRequest, LoginResponse, StudentsListResponse } from "@shared/api";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, init);

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

/** 提交账号密码登录，成功后返回后端角色分流结果。 */
export function login(credentials: LoginRequest): Promise<LoginResponse> {
  return requestJson<LoginResponse>("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(credentials)
  });
}
