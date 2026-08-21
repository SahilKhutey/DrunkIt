/**
 * @drunkit/validation
 * Shared client-side and edge validation schemas for DrunkIt v0.1.
 */

export interface ValidationResult<T> {
  success: boolean;
  data?: T;
  errors?: Record<string, string>;
}

// 1. Auth Validation
export function validateRegistration(data: {
  email?: string;
  password?: string;
  role?: string;
}): ValidationResult<{ email: string; password: string; role: string }> {
  const errors: Record<string, string> = {};

  if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.email = "A valid email address is required.";
  }

  if (!data.password || data.password.length < 8) {
    errors.password = "Password must be at least 8 characters long.";
  }

  const role = (data.role || "CONSUMER").toUpperCase();
  if (!["CONSUMER", "RETAILER", "BRAND_MANAGER", "ADMIN"].includes(role)) {
    errors.role = "Invalid user role specified.";
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors };
  }

  return {
    success: true,
    data: {
      email: data.email!.trim().toLowerCase(),
      password: data.password!,
      role,
    },
  };
}

export function validateLogin(data: {
  email?: string;
  password?: string;
}): ValidationResult<{ email: string; password: string }> {
  const errors: Record<string, string> = {};

  if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.email = "A valid email address is required.";
  }

  if (!data.password || data.password.length < 1) {
    errors.password = "Password cannot be empty.";
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors };
  }

  return {
    success: true,
    data: {
      email: data.email!.trim().toLowerCase(),
      password: data.password!,
    },
  };
}

// 2. Commerce & Checkout Validation
export function validateCheckout(data: {
  idempotency_key?: string;
  channel?: string;
  consumer_age?: number;
  is_age_verified?: boolean;
}): ValidationResult<{
  idempotency_key: string;
  channel: string;
  consumer_age: number;
  is_age_verified: boolean;
}> {
  const errors: Record<string, string> = {};

  if (!data.idempotency_key || data.idempotency_key.trim().length === 0) {
    errors.idempotency_key = "Idempotency key is required to prevent duplicate billing.";
  }

  const channel = (data.channel || "ONLINE_ORDER").toUpperCase();
  if (!["ONLINE_ORDER", "IN_STORE", "HOME_DELIVERY"].includes(channel)) {
    errors.channel = "Invalid fulfillment channel selected.";
  }

  if (!data.is_age_verified) {
    errors.is_age_verified = "Statutory age verification confirmation is mandatory.";
  }

  if (data.consumer_age !== undefined && data.consumer_age < 18) {
    errors.consumer_age = "Consumer must meet the minimum legal drinking age.";
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors };
  }

  return {
    success: true,
    data: {
      idempotency_key: data.idempotency_key!,
      channel,
      consumer_age: data.consumer_age ?? 21,
      is_age_verified: Boolean(data.is_age_verified),
    },
  };
}

// 3. 6-Axis Taste Vector Validation
export function validateTasteVector(data: Record<string, number | undefined>): ValidationResult<{
  body: number;
  sweetness: number;
  smokiness: number;
  bitterness: number;
  fruitiness: number;
  spiciness: number;
}> {
  const dimensions = ["body", "sweetness", "smokiness", "bitterness", "fruitiness", "spiciness"];
  const validated: Record<string, number> = {};
  const errors: Record<string, string> = {};

  for (const dim of dimensions) {
    const val = data[dim];
    if (val !== undefined) {
      if (typeof val !== "number" || val < 0.0 || val > 1.0) {
        errors[dim] = `${dim} must be a float between 0.0 and 1.0.`;
      } else {
        validated[dim] = val;
      }
    } else {
      validated[dim] = 0.5;
    }
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors };
  }

  return {
    success: true,
    data: {
      body: validated.body,
      sweetness: validated.sweetness,
      smokiness: validated.smokiness,
      bitterness: validated.bitterness,
      fruitiness: validated.fruitiness,
      spiciness: validated.spiciness,
    },
  };
}
