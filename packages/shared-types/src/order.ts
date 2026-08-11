export enum OrderStatus {
  CREATED = 'CREATED',
  VALIDATING = 'VALIDATING',
  COMPLIANCE_CHECK = 'COMPLIANCE_CHECK',
  PAYMENT_PENDING = 'PAYMENT_PENDING',
  CONFIRMED = 'CONFIRMED',
  RETAILER_ACCEPTED = 'RETAILER_ACCEPTED',
  PICKING = 'PICKING',
  PACKED = 'PACKED',
  READY_FOR_PICKUP = 'READY_FOR_PICKUP',
  DRIVER_ASSIGNED = 'DRIVER_ASSIGNED',
  IN_TRANSIT = 'IN_TRANSIT',
  DELIVERY_VERIFICATION = 'DELIVERY_VERIFICATION',
  DELIVERED = 'DELIVERED',
  CANCELLED = 'CANCELLED',
  COMPLIANCE_BLOCKED = 'COMPLIANCE_BLOCKED'
}

export interface OrderItem {
  sku: string;
  productName: string;
  category: string;
  abv: number;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

export interface OrderDetails {
  orderId: string;
  consumerId: string;
  storeId: string;
  jurisdiction: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  deliveryFee: number;
  platformFee: number;
  totalAmount: number;
  status: OrderStatus;
  complianceDecisionId?: string;
  deliveryOtp?: string;
  createdAt: string;
  updatedAt: string;
}
