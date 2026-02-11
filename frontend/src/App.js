import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import { useEffect } from "react";
import { Toaster } from "./components/ui/sonner";
import LandingPage from "./pages/LandingPage";
import AuthCallback from "./pages/AuthCallback";
import DemoLogin from "./pages/DemoLogin";
import Dashboard from "./pages/Dashboard";
import StoreSetup from "./pages/StoreSetup";
import Products from "./pages/Products";
import Orders from "./pages/Orders";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import MobileApp from "./pages/MobileApp";
import ONDCIntegration from "./pages/ONDCIntegration";
import Chat from "./pages/Chat";
import ProtectedRoute from "./components/ProtectedRoute";
import PWAInstallPrompt from "./components/PWAInstallPrompt";
import OfflineBanner from "./components/OfflineBanner";
import { registerServiceWorker, onNetworkChange } from "./utils/pwa";
import { toast } from "sonner";
import "./App.css";

function AppRouter() {
  const location = useLocation();
  
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/demo-login" element={<DemoLogin />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/store-setup" element={<ProtectedRoute><StoreSetup /></ProtectedRoute>} />
        <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
        <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
        <Route path="/mobile-app" element={<ProtectedRoute><MobileApp /></ProtectedRoute>} />
        <Route path="/ondc" element={<ProtectedRoute><ONDCIntegration /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
      </Routes>
      <Toaster position="top-right" />
      <PWAInstallPrompt />
      <OfflineBanner />
    </>
  );
}

function App() {
  useEffect(() => {
    // Register service worker for PWA
    registerServiceWorker();
    
    // Monitor network changes
    onNetworkChange((isOnline) => {
      if (isOnline) {
        toast.success('Back online! Syncing data...', { duration: 3000 });
      } else {
        toast.warning('You are offline. Some features may be limited.', { duration: 5000 });
      }
    });
  }, []);

  return (
    <div className="App">
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </div>
  );
}

export default App;
