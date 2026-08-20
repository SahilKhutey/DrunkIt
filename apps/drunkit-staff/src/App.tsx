import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./components/ui/Toast";
import { Layout } from "./components/Layout";
import { ProtectedRoute, AdminOnlyRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { OverviewPage } from "./pages/OverviewPage";
import { RetailersPage } from "./pages/RetailersPage";
import { StoresPage } from "./pages/StoresPage";
import { ListingsPage } from "./pages/ListingsPage";
import { OrdersPage } from "./pages/OrdersPage";
import { DeliveriesPage } from "./pages/DeliveriesPage";

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<OverviewPage />} />
              <Route
                path="retailers"
                element={
                  <AdminOnlyRoute>
                    <RetailersPage />
                  </AdminOnlyRoute>
                }
              />
              <Route path="stores" element={<StoresPage />} />
              <Route path="listings" element={<ListingsPage />} />
              <Route path="orders" element={<OrdersPage />} />
              <Route
                path="deliveries"
                element={
                  <AdminOnlyRoute>
                    <DeliveriesPage />
                  </AdminOnlyRoute>
                }
              />
            </Route>
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}
