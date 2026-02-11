import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Users, Store, Package, ShoppingCart, TrendingUp, MessageCircle,
  Globe, CreditCard, ArrowUpRight
} from 'lucide-react';
import { Button } from '../components/ui/button';
import AdminNav from '../components/AdminNav';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [retailers, setRetailers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      try {
        const userRes = await axios.get(`${API}/auth/me`, { withCredentials: true });
        if (userRes.data.role !== 'admin') {
          navigate('/dashboard');
          return;
        }
        setUser(userRes.data);

        const [metricsRes, retailersRes] = await Promise.all([
          axios.get(`${API}/admin/metrics`, { withCredentials: true }),
          axios.get(`${API}/admin/retailers`, { withCredentials: true }),
        ]);
        setMetrics(metricsRes.data);
        setRetailers(retailersRes.data);
      } catch {
        navigate('/demo-login');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-amber-400" />
      </div>
    );
  }

  const statCards = [
    { label: 'Total Retailers', value: metrics?.total_retailers || 0, icon: Users, color: 'text-blue-400', bg: 'bg-blue-400/10' },
    { label: 'Active Stores', value: metrics?.total_stores || 0, icon: Store, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
    { label: 'Products Listed', value: metrics?.total_products || 0, icon: Package, color: 'text-violet-400', bg: 'bg-violet-400/10' },
    { label: 'Total Orders', value: metrics?.total_orders || 0, icon: ShoppingCart, color: 'text-amber-400', bg: 'bg-amber-400/10' },
    { label: 'Revenue', value: `₹${(metrics?.total_revenue || 0).toLocaleString('en-IN')}`, icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-400/10' },
    { label: 'Chat Messages', value: metrics?.total_chat_messages || 0, icon: MessageCircle, color: 'text-pink-400', bg: 'bg-pink-400/10' },
  ];

  const recentRetailers = retailers
    .filter(r => r.has_store)
    .slice(0, 5);

  return (
    <div className="min-h-screen bg-slate-950" data-testid="admin-dashboard">
      <AdminNav user={user} />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-1">Platform Overview</h1>
          <p className="text-slate-400 text-sm">Real-time metrics for ShopSwift India</p>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8" data-testid="admin-metrics-grid">
          {statCards.map((s) => (
            <div key={s.label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div className={`w-9 h-9 rounded-lg ${s.bg} flex items-center justify-center`}>
                  <s.icon className={`h-4 w-4 ${s.color}`} />
                </div>
              </div>
              <p className="text-2xl font-bold text-white">{s.value}</p>
              <p className="text-xs text-slate-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Subscription breakdown */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-amber-400" /> Subscriptions
            </h2>
            <div className="space-y-3">
              {[
                { label: 'Active / Trial', value: metrics?.subscriptions?.active || 0, color: 'bg-emerald-500' },
                { label: 'Expired', value: metrics?.subscriptions?.expired || 0, color: 'bg-red-500' },
                { label: 'Cancelled', value: metrics?.subscriptions?.cancelled || 0, color: 'bg-slate-500' },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                    <span className="text-sm text-slate-300">{item.label}</span>
                  </div>
                  <span className="text-sm font-semibold text-white">{item.value}</span>
                </div>
              ))}
              <hr className="border-slate-800" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">By Tier</span>
              </div>
              {[
                { label: 'Basic', value: metrics?.tiers?.basic || 0 },
                { label: 'Pro', value: metrics?.tiers?.pro || 0 },
                { label: 'Premium', value: metrics?.tiers?.premium || 0 },
              ].map((t) => (
                <div key={t.label} className="flex items-center justify-between pl-4">
                  <span className="text-sm text-slate-400">{t.label}</span>
                  <span className="text-sm font-medium text-slate-300">{t.value}</span>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center gap-2">
              <Globe className="h-4 w-4 text-blue-400" />
              <span className="text-sm text-slate-400">ONDC-enabled stores:</span>
              <span className="text-sm font-semibold text-white">{metrics?.ondc_enabled_stores || 0}</span>
            </div>
          </div>

          {/* Recent retailers */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Users className="h-4 w-4 text-blue-400" /> Recent Retailers
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/admin/retailers')}
                className="text-amber-400 hover:text-amber-300 text-xs"
                data-testid="view-all-retailers-btn"
              >
                View All <ArrowUpRight className="h-3 w-3 ml-1" />
              </Button>
            </div>
            <div className="space-y-2">
              {recentRetailers.map((r) => (
                <button
                  key={r.user_id}
                  onClick={() => navigate('/admin/retailers', { state: { selectedId: r.user_id } })}
                  className="w-full text-left flex items-center gap-3 p-3 rounded-lg hover:bg-slate-800/50 transition-colors"
                  data-testid={`retailer-row-${r.user_id}`}
                >
                  <div className="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs font-semibold text-blue-400">{r.name?.[0]?.toUpperCase()}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{r.store_name || r.name}</p>
                    <p className="text-xs text-slate-500">{r.email}</p>
                  </div>
                  <StatusBadge status={r.subscription_status} />
                </button>
              ))}
              {recentRetailers.length === 0 && (
                <p className="text-sm text-slate-500 text-center py-4">No retailers yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const styles = {
    active: 'bg-emerald-500/10 text-emerald-400',
    trial: 'bg-amber-500/10 text-amber-400',
    expired: 'bg-red-500/10 text-red-400',
    cancelled: 'bg-slate-500/10 text-slate-400',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${styles[status] || styles.trial}`}>
      {status || 'none'}
    </span>
  );
}
