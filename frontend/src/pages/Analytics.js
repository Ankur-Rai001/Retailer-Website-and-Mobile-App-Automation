import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, TrendingUp, Package, ShoppingCart, IndianRupee } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Analytics() {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/analytics/overview`, { withCredentials: true });
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
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
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/dashboard')}
              data-testid="back-button"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-2xl font-bold text-secondary">Analytics</h1>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-primary/10 rounded-lg">
                <Package className="h-8 w-8 text-primary" />
              </div>
            </div>
            <p className="text-3xl font-bold text-secondary mb-1">{analytics?.total_products || 0}</p>
            <p className="text-sm text-muted">Total Products</p>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-accent/10 rounded-lg">
                <ShoppingCart className="h-8 w-8 text-accent" />
              </div>
            </div>
            <p className="text-3xl font-bold text-secondary mb-1">{analytics?.total_orders || 0}</p>
            <p className="text-sm text-muted">Total Orders</p>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-primary/10 rounded-lg">
                <IndianRupee className="h-8 w-8 text-primary" />
              </div>
            </div>
            <p className="text-3xl font-bold text-secondary mb-1">₹{analytics?.total_revenue?.toLocaleString('en-IN') || 0}</p>
            <p className="text-sm text-muted">Total Revenue</p>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-orange-500/10 rounded-lg">
                <TrendingUp className="h-8 w-8 text-orange-500" />
              </div>
            </div>
            <p className="text-3xl font-bold text-secondary mb-1">{analytics?.pending_orders || 0}</p>
            <p className="text-sm text-muted">Pending Orders</p>
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <div className="bg-white border border-slate-200 rounded-xl p-8">
            <h2 className="text-xl font-semibold text-secondary mb-6">Business Overview</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <span className="text-muted">Active Products</span>
                <span className="text-lg font-bold text-secondary">{analytics?.total_products || 0}</span>
              </div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <span className="text-muted">Completed Orders</span>
                <span className="text-lg font-bold text-accent">{(analytics?.total_orders || 0) - (analytics?.pending_orders || 0)}</span>
              </div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <span className="text-muted">Average Order Value</span>
                <span className="text-lg font-bold text-secondary">
                  ₹{analytics?.total_orders > 0 ? Math.round(analytics.total_revenue / analytics.total_orders).toLocaleString('en-IN') : 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted">Success Rate</span>
                <span className="text-lg font-bold text-accent">
                  {analytics?.total_orders > 0 ? Math.round(((analytics.total_orders - analytics.pending_orders) / analytics.total_orders) * 100) : 0}%
                </span>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20 rounded-xl p-8">
            <h2 className="text-xl font-semibold text-secondary mb-4">Growth Tips</h2>
            <div className="space-y-4">
              <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4">
                <h3 className="font-semibold text-secondary mb-2">Add More Products</h3>
                <p className="text-sm text-muted">Expand your catalog to attract more customers and increase sales opportunities.</p>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4">
                <h3 className="font-semibold text-secondary mb-2">Share Your Store</h3>
                <p className="text-sm text-muted">Promote your store link on WhatsApp, Facebook, and Instagram to reach more customers.</p>
              </div>
              <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4">
                <h3 className="font-semibold text-secondary mb-2">Enable ONDC</h3>
                <p className="text-sm text-muted">Join ONDC network to reach customers on PhonePe, Paytm, and other platforms.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
