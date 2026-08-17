export interface Price {
  mrp: number;
  selling_price: number;
  discount_percentage: number;
}

export interface ListingCard {
  listing_id: string;
  product_id: string;
  name: string;
  brand: string;
  category: string;
  variant: string | null;
  pack_size: string;
  image_url: string | null;
  price: Price;
  availability_status: "IN_STOCK" | "LOW_STOCK" | "OUT_OF_STOCK";
  store_id: string;
  store_name: string;
  eta_min_minutes: number;
  eta_max_minutes: number;
  seller_verified: boolean;
  can_view: boolean;
  can_add_to_cart: boolean;
  eligibility_reason: string;
}

export interface Me {
  consumer_id: string;
  phone: string;
  state: string | null;
  eligibility_state: "NOT_STARTED" | "VERIFIED" | "FAILED" | "EXPIRED";
  minimum_age_required: number | null;
}

export interface EligibilityResult {
  decision: string;
  can_view: boolean;
  can_add_to_cart: boolean;
  can_checkout: boolean;
  reason: string;
  minimum_age_required: number | null;
  state: string;
}

export interface OrderItemView {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
}

export interface OrderView {
  id: string;
  status: string;
  subtotal: number;
  delivery_fee: number;
  total: number;
  items: OrderItemView[];
}

export interface OrderSummary {
  id: string;
  status: string;
  total: number;
  item_count: number;
  created_at: string;
}

export interface DeliveryView {
  id: string;
  order_id: string;
  status:
    | "REQUESTED"
    | "ASSIGNED"
    | "PICKED_UP"
    | "IN_TRANSIT"
    | "ARRIVING"
    | "HANDOFF_VERIFICATION"
    | "DELIVERED"
    | "FAILED"
    | "CANCELLED";
  eta_min_minutes: number | null;
  eta_max_minutes: number | null;
  handoff_verified: boolean;
  failure_reason: string | null;
}

export interface CartLine {
  product_id: string;
  quantity: number;
  name: string;
  unit_price: number;
  pack_size: string;
  store_id: string;
  store_name: string;
}

export interface ApiError {
  code: string;
  message: string;
}
