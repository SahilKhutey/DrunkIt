import type {
  StaffMe,
  RetailerView,
  StoreView,
  ProductView,
  AdminListingView,
  AdminOrderView,
  AdminDeliveryView,
  StaffAccountView,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

const TOKEN_KEY = "drunkit_staff_access_token";

export class ApiRequestError extends Error {
  code: string;
  status: number;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
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
  if (auth && token) headers["Authorization"] = `Bearer ${token}`;

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
      if (typeof data.detail === "string") message = data.detail;
      else if (data.detail && typeof data.detail === "object") {
        code = data.detail.code ?? code;
        message = data.detail.message ?? message;
      }
    } catch {
      // non-JSON response — keep default message
    }
    throw new ApiRequestError(res.status, code, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string; staff_id: string; role: string; retailer_id: string | null }>(
      "/v1/admin/auth/login",
      { method: "POST", body: { email, password }, auth: false }
    ),

  me: () => request<StaffMe>("/v1/admin/auth/me"),

  listRetailers: () => request<RetailerView[]>("/v1/admin/retailers"),
  createRetailer: (name: string, license_number?: string) =>
    request<{ retailer_id: string; status: string }>("/v1/admin/retailers", {
      method: "POST",
      body: { name, license_number },
    }),
  verifyRetailer: (retailerId: string) =>
    request<{ retailer_id: string; status: string }>(`/v1/admin/retailers/${retailerId}/verify`, {
      method: "POST",
    }),
  listRetailerStaff: (retailerId: string) =>
    request<StaffAccountView[]>(`/v1/admin/retailers/${retailerId}/staff`),
  createRetailerStaff: (retailerId: string, email: string, password: string) =>
    request<{ staff_id: string; email: string }>(`/v1/admin/retailers/${retailerId}/staff`, {
      method: "POST",
      body: { email, password },
    }),

  listStores: (retailerId?: string) =>
    request<StoreView[]>("/v1/admin/stores", { params: { retailer_id: retailerId } }),
  createStore: (payload: {
    retailer_id: string;
    name: string;
    state: string;
    city: string;
    latitude: number;
    longitude: number;
  }) => request<{ store_id: string }>("/v1/admin/stores", { method: "POST", body: payload }),

  listProducts: () => request<ProductView[]>("/v1/admin/products"),
  createProduct: (payload: {
    name: string;
    brand: string;
    category: string;
    variant?: string;
    pack_size: string;
    abv_percent?: number;
  }) => request<{ product_id: string }>("/v1/admin/products", { method: "POST", body: payload }),

  listListings: (storeId: string) =>
    request<AdminListingView[]>("/v1/admin/listings", { params: { store_id: storeId } }),
  upsertListing: (payload: {
    store_id: string;
    product_id: string;
    mrp: number;
    selling_price: number;
    quantity: number;
  }) => request<{ listing_id: string; status: string }>("/v1/admin/listings", { method: "POST", body: payload }),

  listOrders: (storeId: string) =>
    request<AdminOrderView[]>("/v1/admin/orders", { params: { store_id: storeId } }),

  listDeliveries: (status?: string) =>
    request<AdminDeliveryView[]>("/v1/admin/deliveries", { params: { status } }),
  assignDriver: (deliveryId: string, driverName: string, driverPhone: string) =>
    request(`/v1/admin/deliveries/${deliveryId}/assign`, {
      method: "POST",
      params: { driver_name: driverName, driver_phone: driverPhone },
    }),
  transitionDelivery: (deliveryId: string, newStatus: string) =>
    request(`/v1/admin/deliveries/${deliveryId}/transition`, {
      method: "POST",
      body: { new_status: newStatus },
    }),
  verifyHandoff: (deliveryId: string, verified: boolean, reason?: string) =>
    request(`/v1/admin/deliveries/${deliveryId}/handoff`, {
      method: "POST",
      body: { verified, reason },
    }),
};
