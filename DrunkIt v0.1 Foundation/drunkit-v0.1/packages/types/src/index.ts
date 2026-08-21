/**
 * @drunkit/types
 * Canonical frontend and SDK domain and API contracts for DrunkIt v0.1.
 */

// 1. Identity & RBAC
export type UserRole = "CONSUMER" | "RETAILER" | "BRAND_MANAGER" | "ADMIN";

export interface User {
  id: string;
  email: string;
  phone?: string | null;
  role: UserRole;
  status: string;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 2. Catalog & Taste Intelligence
export interface TasteProfile {
  body: number;
  sweetness: number;
  smokiness: number;
  bitterness: number;
  fruitiness: number;
  spiciness: number;
}

export interface SKU {
  id: string;
  variant_id: string;
  canonical_code: string;
  barcode?: string | null;
  status: string;
}

export interface ProductVariant {
  id: string;
  product_id: string;
  volume_ml: number;
  package_type: string;
  status: string;
  skus: SKU[];
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  country_code: string;
  description?: string | null;
  status: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  parent_id?: string | null;
}

export interface Product {
  id: string;
  brand_id?: string | null;
  brand_name?: string | null;
  category_id?: string | null;
  category_name?: string | null;
  name: string;
  slug: string;
  description?: string | null;
  product_type: string;
  region?: string | null;
  country_of_origin: string;
  abv?: number | string | null;
  status: string;
  created_at: string;
  variants?: ProductVariant[];
  taste_profile?: TasteProfile | null;
}

// 3. Retailer & Live Availability
export interface RetailerLocation {
  id: string;
  retailer_id: string;
  name: string;
  address: string;
  city: string;
  state_code: string;
  postal_code: string;
  country_code: string;
  latitude?: number | null;
  longitude?: number | null;
  status: string;
}

export interface StoreAvailabilityItem {
  retailer_sku_id: string;
  sku_id: string;
  sku_code: string;
  volume_ml: number;
  location_id: string;
  location_name: string;
  city: string;
  state_code: string;
  distance_km?: number | null;
  availability_status: "IN_STOCK" | "LOW_STOCK" | "OUT_OF_STOCK";
  quantity: number;
  amount_minor: number;
  currency: string;
  price_formatted: string;
}

export interface ProductAvailabilityResponse {
  product_id: string;
  product_name: string;
  product_slug: string;
  stores_count: number;
  stores: StoreAvailabilityItem[];
}

// 4. Discovery & Occasions
export interface OccasionCollection {
  slug: string;
  title: string;
  subtitle: string;
  hero_tag: string;
  item_count: number;
  items: Product[];
}

export interface TasteMatchQuery {
  body?: number;
  sweetness?: number;
  smokiness?: number;
  bitterness?: number;
  fruitiness?: number;
  spiciness?: number;
  preferred_types?: string[];
  min_abv?: number;
  max_abv?: number;
  limit?: number;
}

export interface TasteMatchResult {
  product: Product;
  similarity_score: number;
  match_reasons: string[];
  taste_profile?: TasteProfile | null;
}

// 5. Compliance
export type ComplianceDecisionType = "ALLOWED" | "DENIED" | "REQUIRES_VERIFICATION";

export interface ComplianceCheckRequest {
  correlation_id?: string;
  jurisdiction_code: string;
  consumer_id?: string;
  consumer_age?: number | null;
  is_age_verified?: boolean;
  retailer_id?: string;
  retailer_location_id?: string;
  product_id?: string;
  sku_id?: string;
  product_class?: string;
  channel?: "ONLINE_ORDER" | "IN_STORE" | "HOME_DELIVERY";
  quantity?: number;
  total_volume_ml?: number;
  current_time?: string;
}

export interface ComplianceDecisionResponse {
  check_id: string;
  correlation_id: string;
  jurisdiction_code: string;
  decision: ComplianceDecisionType;
  reason_codes: string[];
  required_checks: string[];
  rule_set_version: string;
  decided_at: string;
}

// 6. Commerce & Orders
export interface CartItem {
  id: string;
  sku_id: string;
  canonical_code: string;
  product_name: string;
  volume_ml: number;
  retailer_location_id: string;
  retailer_name: string;
  quantity: number;
  unit_price_minor: number;
  unit_price_formatted: string;
  total_price_minor: number;
  total_price_formatted: string;
}

export interface Cart {
  id: string;
  consumer_id: string;
  jurisdiction_id?: string | null;
  items: CartItem[];
  item_count: number;
  subtotal_minor: number;
  subtotal_formatted: string;
  total_volume_ml: number;
  status: string;
}

export interface OrderItem {
  id: string;
  sku_id: string;
  canonical_code: string;
  product_name: string;
  volume_ml: number;
  quantity: number;
  unit_price_minor: number;
  unit_price_formatted: string;
  total_price_minor: number;
  total_price_formatted: string;
}

export interface Order {
  id: string;
  consumer_id: string;
  retailer_location_id: string;
  retailer_name: string;
  status: "PENDING" | "CONFIRMED" | "PREPARING" | "READY_FOR_PICKUP" | "OUT_FOR_DELIVERY" | "FULFILLED" | "CANCELLED";
  currency: string;
  subtotal_minor: number;
  total_minor: number;
  total_formatted: string;
  compliance_decision_id?: string | null;
  idempotency_key: string;
  items: OrderItem[];
  created_at: string;
}

// 7. Event Envelope (Outbox)
export interface EventEnvelope<T = Record<string, unknown>> {
  id: string;
  event_type: string;
  aggregate_type: string;
  aggregate_id: string;
  correlation_id: string;
  payload: T;
  created_at: string;
}
