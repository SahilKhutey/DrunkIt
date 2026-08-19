import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import { ToastProvider } from "./components/ui/Toast";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { HomePage } from "./pages/HomePage";
import { SearchPage } from "./pages/SearchPage";
import { ProductDetailPage } from "./pages/ProductDetailPage";
import { LoginPage } from "./pages/LoginPage";
import { EligibilityPage } from "./pages/EligibilityPage";
import { AccountPage } from "./pages/AccountPage";
import { CartPage } from "./pages/CartPage";
import { CheckoutPage } from "./pages/CheckoutPage";
import { OrderTrackingPage } from "./pages/OrderTrackingPage";
import { OrderHistoryPage } from "./pages/OrderHistoryPage";
import { AboutPage } from "./pages/AboutPage";
import { ResponsibleDrinkingPage } from "./pages/ResponsibleDrinkingPage";
import { NotFoundPage } from "./pages/NotFoundPage";

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <CartProvider>
          <ToastProvider>
            <BrowserRouter>
              <div className="flex min-h-screen flex-col">
                <Navbar />
                <div className="flex-1">
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/search" element={<SearchPage />} />
                    <Route path="/product/:listingId" element={<ProductDetailPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/eligibility" element={<EligibilityPage />} />
                    <Route path="/account" element={<AccountPage />} />
                    <Route path="/cart" element={<CartPage />} />
                    <Route path="/checkout" element={<CheckoutPage />} />
                    <Route path="/orders" element={<OrderHistoryPage />} />
                    <Route path="/orders/:orderId" element={<OrderTrackingPage />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/responsible-drinking" element={<ResponsibleDrinkingPage />} />
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>
                </div>
                <Footer />
              </div>
            </BrowserRouter>
          </ToastProvider>
        </CartProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
