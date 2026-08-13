import { createClient } from "@faccp/api-client";

const TOKEN_KEY = "faccp_driver_token";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export const apiClient = createClient(
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  () => getToken()
);

export function setDriverToken(token: string) {
  if (typeof window !== "undefined") localStorage.setItem(TOKEN_KEY, token);
}

export function clearDriverToken() {
  if (typeof window !== "undefined") localStorage.removeItem(TOKEN_KEY);
}
