import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, setToken } from "../api/client";
import type { Me } from "../types/api";

interface AuthContextValue {
  me: Me | null;
  loading: boolean;
  deliveryState: string | null;
  setDeliveryState: (state: string) => void;
  refreshMe: () => Promise<void>;
  logout: () => void;
  isLoggedIn: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const STATE_STORAGE_KEY = "drunkit_delivery_state";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);
  const [deliveryState, setDeliveryStateInner] = useState<string | null>(
    () => localStorage.getItem(STATE_STORAGE_KEY)
  );

  const refreshMe = useCallback(async () => {
    const hasToken = !!localStorage.getItem("drunkit_access_token");
    if (!hasToken) {
      setMe(null);
      setLoading(false);
      return;
    }
    try {
      const profile = await api.me();
      setMe(profile);
      if (profile.state) {
        setDeliveryStateInner(profile.state);
        localStorage.setItem(STATE_STORAGE_KEY, profile.state);
      }
    } catch {
      // Invalid/expired session — clear it so the app treats the
      // person as logged out rather than looping on failed calls.
      setToken(null);
      setMe(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshMe();
  }, [refreshMe]);

  const setDeliveryState = useCallback((state: string) => {
    setDeliveryStateInner(state);
    localStorage.setItem(STATE_STORAGE_KEY, state);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setMe(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ me, loading, deliveryState, setDeliveryState, refreshMe, logout, isLoggedIn: !!me }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
