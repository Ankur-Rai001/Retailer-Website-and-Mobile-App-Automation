import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Store, Package, ShoppingCart, TrendingUp, Plus, Settings, LogOut, BarChart3 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  const navigate = useNavigate();
  const [store, setStore] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [userRes, storeRes] = await Promise.all([
        axios.get(`${API}/auth/me`, { withCredentials: true }),
        axios.get(`${API}/stores/my-store`, { withCredentials: true })
      ]);
      
      setUser(userRes.data);
      setStore(storeRes.data);
      
      const analyticsRes = await axios.get(`${API}/analytics/overview`, { withCredentials: true });
      setAnalytics(analyticsRes.data);
    } catch (error) {
      if (error.response?.status === 404) {
        navigate('/store-setup');
      } else {
        toast.error('Failed to load dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      navigate('/');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Store className="h-6 w-6 text-primary" />
              <span className="font-heading text-xl font-bold text-secondary">ShopSwift</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted">{user?.name}</span>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleLogout}
                data-testid="logout-button"
                className="text-muted hover:text-secondary"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-secondary mb-2">Welcome back, {user?.name?.split(' ')[0]}!</h1>
          <p className="text-slate-600">Here's what's happening with {store?.store_name}</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <Package className="h-10 w-10 text-primary" />
              <div className="text-right">
                <p className="text-3xl font-bold text-secondary">{analytics?.total_products || 0}</p>
                <p className="text-sm text-muted">Products</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <ShoppingCart className="h-10 w-10 text-accent" />
              <div className="text-right">
                <p className="text-3xl font-bold text-secondary">{analytics?.total_orders || 0}</p>
                <p className="text-sm text-muted">Total Orders</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="h-10 w-10 text-primary" />
              <div className="text-right">
                <p className="text-3xl font-bold text-secondary">₹{analytics?.total_revenue?.toLocaleString('en-IN') || 0}</p>
                <p className="text-sm text-muted">Revenue</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <ShoppingCart className="h-10 w-10 text-orange-500" />
              <div className="text-right">
                <p className="text-3xl font-bold text-secondary">{analytics?.pending_orders || 0}</p>
                <p className="text-sm text-muted">Pending</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white border border-slate-200 rounded-xl p-8">
            <h2 className="text-2xl font-semibold text-secondary mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Button 
                onClick={() => navigate('/products')}
                data-testid="add-product-button"
                className="w-full justify-start bg-primary text-white hover:bg-primary/90 rounded-lg h-12"
              >
                <Plus className="h-5 w-5 mr-2" />
                Add New Product
              </Button>
              <Button 
                onClick={() => navigate('/orders')}
                variant="outline"
                className="w-full justify-start rounded-lg h-12"
              >
                <ShoppingCart className="h-5 w-5 mr-2" />
                View Orders
              </Button>
              <Button 
                onClick={() => navigate('/analytics')}
                variant="outline"
                className="w-full justify-start rounded-lg h-12"
              >
                <BarChart3 className="h-5 w-5 mr-2" />
                View Analytics
              </Button>
              <Button 
                onClick={() => navigate('/settings')}
                variant="outline"
                className="w-full justify-start rounded-lg h-12"
              >
                <Settings className="h-5 w-5 mr-2" />
                Store Settings
              </Button>
            </div>
          </div>

          <div className="bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20 rounded-xl p-8">
            <h2 className="text-2xl font-semibold text-secondary mb-4">Your Store</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted">Store Name</p>
                <p className="text-lg font-semibold text-secondary">{store?.store_name}</p>
              </div>
              <div>
                <p className="text-sm text-muted">Store URL</p>
                <p className="text-lg font-mono text-primary">{store?.subdomain}.shopswift.in</p>
              </div>
              <div>
                <p className="text-sm text-muted">Category</p>
                <p className="text-lg font-semibold text-secondary capitalize">{store?.category}</p>
              </div>
              <div>
                <p className="text-sm text-muted">Subscription</p>
                <span className="inline-block px-3 py-1 bg-accent text-white rounded-full text-sm font-semibold capitalize">
                  {store?.subscription_tier}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-secondary">Getting Started Tips</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mb-3">
                <Package className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold text-secondary">Add Products</h3>
              <p className="text-sm text-muted">Start by adding your products with images, prices, and stock levels.</p>
            </div>
            <div className="space-y-2">
              <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center mb-3">
                <Settings className="h-5 w-5 text-accent" />
              </div>
              <h3 className="font-semibold text-secondary">Customize Store</h3>
              <p className="text-sm text-muted">Choose a template, upload your logo, and customize your store appearance.</p>
            </div>
            <div className="space-y-2">
              <div className="w-10 h-10 bg-orange-500/10 rounded-full flex items-center justify-center mb-3">
                <TrendingUp className="h-5 w-5 text-orange-500" />
              </div>
              <h3 className="font-semibold text-secondary">Share Your Store</h3>
              <p className="text-sm text-muted">Share your store link on WhatsApp, Facebook, and Instagram to start getting orders.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
