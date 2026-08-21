/**
 * @drunkit/api-client
 * Universal, typed HTTP client for the DrunkIt v0.1 Platform.
 */

import type {
  AuthTokenResponse,
  Cart,
  ComplianceCheckRequest,
  ComplianceDecisionResponse,
  OccasionCollection,
  Order,
  Product,
  ProductAvailabilityResponse,
  TasteMatchQuery,
  TasteMatchResult,
  User,
} from "@drunkit/types";

export interface ApiClientConfig {
  baseUrl?: string;
  token?: string;
}

export class DrunkItApiClient {
  private baseUrl: string;
  private token: string | null;

  constructor(config?: ApiClientConfig) {
    this.baseUrl = config?.baseUrl || "http://127.0.0.1:8000/api/v1";
    this.token = config?.token || null;
  }

  public setToken(token: string | null): void {
    this.token = token;
  }

  private async request<T>(path: string, options?: RequestInit): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options?.headers as Record<string, string>),
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data?.error?.message || `Request failed with status ${response.status}`;
      throw new Error(errorMsg);
    }

    return data as T;
  }

  // 1. Auth & Identity
  public auth = {
    register: (payload: { email: string; password: string; role?: string }) =>
      this.request<AuthTokenResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      }),

    login: (payload: { email: string; password: string }) =>
      this.request<AuthTokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      }),

    getMe: () => this.request<User>("/auth/me"),
  };

  // 2. Catalog & Products
  public catalog = {
    listProducts: (params?: { q?: string; product_type?: string; limit?: number }) => {
      const query = new URLSearchParams();
      if (params?.q) query.set("q", params.q);
      if (params?.product_type) query.set("product_type", params.product_type);
      if (params?.limit) query.set("limit", params.limit.toString());
      return this.request<{ items: Product[]; total: number }>(`/products?${query.toString()}`);
    },

    getProduct: (idOrSlug: string) => this.request<Product>(`/products/${idOrSlug}`),

    getProductAvailability: (idOrSlug: string, coords?: { lat: number; lon: number }) => {
      const query = new URLSearchParams();
      if (coords) {
        query.set("latitude", coords.lat.toString());
        query.set("longitude", coords.lon.toString());
      }
      return this.request<ProductAvailabilityResponse>(
        `/products/${idOrSlug}/availability?${query.toString()}`
      );
    },
  };

  // 3. Discovery & Occasions
  public discovery = {
    getFeed: () => this.request<any>("/discovery/feed"),
    listOccasions: () => this.request<OccasionCollection[]>("/discovery/occasions"),
    getOccasion: (slug: string) => this.request<OccasionCollection>(`/discovery/occasions/${slug}`),
    matchTaste: (query: TasteMatchQuery) =>
      this.request<TasteMatchResult[]>("/discovery/taste-match", {
        method: "POST",
        body: JSON.stringify(query),
      }),
  };

  // 4. Deterministic Compliance
  public compliance = {
    check: (payload: ComplianceCheckRequest) =>
      this.request<ComplianceDecisionResponse>("/compliance/check", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    listJurisdictions: () => this.request<any[]>("/compliance/jurisdictions"),
  };

  // 5. Commerce, Cart & Orders
  public commerce = {
    getCart: () => this.request<Cart>("/cart"),

    addToCart: (skuId: string, retailerLocationId: string, quantity = 1) =>
      this.request<Cart>("/cart/items", {
        method: "POST",
        body: JSON.stringify({
          sku_id: skuId,
          retailer_location_id: retailerLocationId,
          quantity,
        }),
      }),

    removeFromCart: (itemId: string) =>
      this.request<Cart>(`/cart/items/${itemId}`, {
        method: "DELETE",
      }),

    checkout: (payload: {
      idempotency_key: string;
      channel?: string;
      consumer_age?: number;
      is_age_verified?: boolean;
    }) =>
      this.request<Order>("/cart/checkout", {
        method: "POST",
        body: JSON.stringify(payload),
      }),

    listOrders: () => this.request<Order[]>("/orders"),
    getOrder: (orderId: string) => this.request<Order>(`/orders/${orderId}`),
  };
}

export default DrunkItApiClient;
