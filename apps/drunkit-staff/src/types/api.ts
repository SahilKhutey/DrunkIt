export interface StaffMe {
  staff_id: string;
  email: string;
  role: "PLATFORM_ADMIN" | "RETAILER_STAFF";
  retailer_id: string | null;
}

export interface RetailerView {
  id: string;
  name: string;
  license_number: string | null;
  status: "PENDING" | "VERIFIED" | "SUSPENDED";
  created_at: string;
}

export interface StoreView {
  id: string;
  retailer_id: string;
  retailer_name: string;
  name: string;
  state: string;
  city: string;
  latitude: number;
  longitude: number;
  is_open: boolean;
  active: boolean;
}

export interface ProductView {
  id: string;
  name: string;
  brand: string;
  category: string;
  variant: string | null;
  pack_size: string;
  active: boolean;
}

export interface AdminListingView {
  listing_id: string;
  store_id: string;
  product_id: string;
  product_name: string;
  brand: string;
  pack_size: string;
  status: string;
  mrp: number | null;
  selling_price: number | null;
  quantity: number | null;
}

export interface AdminOrderItemView {
  product_name: string;
  quantity: number;
  unit_price: number;
}

export interface AdminOrderView {
  id: string;
  status: string;
  total: number;
  created_at: string;
  delivery_address: string;
  items: AdminOrderItemView[];
}

export interface AdminDeliveryView {
  id: string;
  order_id: string;
  store_id: string;
  store_name: string;
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
  driver_name: string | null;
  driver_phone: string | null;
  eta_min_minutes: number | null;
  eta_max_minutes: number | null;
  created_at: string;
}

export interface StaffAccountView {
  id: string;
  email: string;
  role: string;
  retailer_id: string | null;
  active: boolean;
  created_at: string;
}
