import type {
  Me,
  EligibilityResult,
  ListingCard,
  OrderView,
  OrderSummary,
  DeliveryView,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiRequestError extends Error {
  code: string;
  status: number;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function getToken(): string | null {
  return localStorage.getItem("drunkit_access_token");
}

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem("drunkit_access_token", token);
  } else {
    localStorage.removeItem("drunkit_access_token");
  }
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown; params?: Record<string, string | undefined>; auth?: boolean } = {}
): Promise<T> {
  const { method = "GET", body, params, auth = true } = options;

  let url = `${API_BASE_URL}${path}`;
  if (params) {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined) qs.set(k, v);
    });
    const qsString = qs.toString();
    if (qsString) url += `?${qsString}`;
  }

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (auth && token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let code = "UNKNOWN_ERROR";
    let message = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (data.detail && typeof data.detail === "object") {
        code = data.detail.code ?? code;
        message = data.detail.message ?? message;
      }
    } catch {
      // response wasn't JSON — keep the default message
    }
    throw new ApiRequestError(res.status, code, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  requestOtp: (phone: string) =>
    request<{ request_id: string; expires_in_seconds: number; dev_otp: string | null }>(
      "/v1/auth/otp/request",
      { method: "POST", body: { phone }, auth: false }
    ),

  verifyOtp: (phone: string, code: string) =>
    request<{ access_token: string; token_type: string; consumer_id: string }>("/v1/auth/otp/verify", {
      method: "POST",
      body: { phone, code },
      auth: false,
    }),

  me: () => request<Me>("/v1/me"),

  verifyEligibility: (state: string, date_of_birth: string) =>
    request<EligibilityResult>("/v1/eligibility/verify", {
      method: "POST",
      body: { state, date_of_birth },
    }),

  listListings: (lat: number, lng: number, state: string, category?: string) =>
    request<ListingCard[]>("/v1/listings", {
      params: { lat: String(lat), lng: String(lng), state, category },
    }),

  getListing: (listingId: string) => request<ListingCard>(`/v1/listings/${listingId}`),

  placeOrder: (payload: {
    store_id: string;
    items: { product_id: string; quantity: number }[];
    delivery_address: string;
    delivery_latitude: number;
    delivery_longitude: number;
  }) => request<OrderView>("/v1/orders", { method: "POST", body: payload }),

  listOrders: () => request<OrderSummary[]>("/v1/orders"),

  getOrder: (orderId: string) => request<OrderView>(`/v1/orders/${orderId}`),

  getDelivery: (orderId: string) => request<DeliveryView>(`/v1/orders/${orderId}/delivery`),
};
