import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, setToken, getToken } from "../api/client";
import type { StaffMe } from "../types/api";

interface AuthContextValue {
  me: StaffMe | null;
  loading: boolean;
  isLoggedIn: boolean;
  isPlatformAdmin: boolean;
  refreshMe: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<StaffMe | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    if (!getToken()) {
      setMe(null);
      setLoading(false);
      return;
    }
    try {
      const profile = await api.me();
      setMe(profile);
    } catch {
      setToken(null);
      setMe(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshMe();
  }, [refreshMe]);

  const logout = useCallback(() => {
    setToken(null);
    setMe(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        me,
        loading,
        isLoggedIn: !!me,
        isPlatformAdmin: me?.role === "PLATFORM_ADMIN",
        refreshMe,
        logout,
      }}
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
