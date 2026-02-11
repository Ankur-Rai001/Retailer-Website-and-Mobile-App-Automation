import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import {
  Users, Search, Store, Package, ShoppingCart, ChevronRight,
  ArrowLeft, X, Globe, Mail, Phone
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import AdminNav from '../components/AdminNav';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminRetailers() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [retailers, setRetailers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterTier, setFilterTier] = useState('');
  const [selectedRetailer, setSelectedRetailer] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        const userRes = await axios.get(`${API}/auth/me`, { withCredentials: true });
        if (userRes.data.role !== 'admin') { navigate('/dashboard'); return; }
        setUser(userRes.data);
        await fetchRetailers();
      } catch {
        navigate('/demo-login');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, [navigate]);

  // Auto-select retailer if navigated with state
  useEffect(() => {
    if (location.state?.selectedId && retailers.length > 0) {
      const r = retailers.find(x => x.user_id === location.state.selectedId);
      if (r) loadDetail(r);
    }
  }, [location.state, retailers]);

  const fetchRetailers = async () => {
    const params = new URLSearchParams();
    if (search) params.set('search', search);
    if (filterStatus) params.set('status', filterStatus);
    if (filterTier) params.set('tier', filterTier);
    const res = await axios.get(`${API}/admin/retailers?${params}`, { withCredentials: true });
    setRetailers(res.data);
  };

  const loadDetail = async (r) => {
    setSelectedRetailer(r);
    setDetailLoading(true);
    try {
      const res = await axios.get(`${API}/admin/retailers/${r.user_id}`, { withCredentials: true });
      setDetail(res.data);
    } catch {
      toast.error('Failed to load retailer details');
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => {
    if (!loading) fetchRetailers();
  }, [search, filterStatus, filterTier]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-amber-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950" data-testid="admin-retailers-page">
      <AdminNav user={user} />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white mb-1">Manage Retailers</h1>
          <p className="text-slate-400 text-sm">{retailers.length} retailer(s) on the platform</p>
        </div>

        <div className="flex flex-col lg:flex-row gap-6" style={{ height: 'calc(100vh - 180px)' }}>
          {/* List panel */}
          <div className={`lg:w-[420px] flex flex-col ${selectedRetailer ? 'hidden lg:flex' : 'flex'}`}>
            {/* Filters */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 mb-4 space-y-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <Input
                  placeholder="Search by name or email..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
                  data-testid="retailer-search"
                />
              </div>
              <div className="flex gap-2">
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="flex-1 text-sm bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-2"
                  data-testid="filter-status"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="trial">Trial</option>
                  <option value="expired">Expired</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                <select
                  value={filterTier}
                  onChange={(e) => setFilterTier(e.target.value)}
                  className="flex-1 text-sm bg-slate-800 border border-slate-700 text-slate-300 rounded-lg px-3 py-2"
                  data-testid="filter-tier"
                >
                  <option value="">All Tiers</option>
                  <option value="basic">Basic</option>
                  <option value="pro">Pro</option>
                  <option value="premium">Premium</option>
                </select>
              </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto bg-slate-900 border border-slate-800 rounded-xl">
              {retailers.filter(r => r.has_store).length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-center p-4">
                  <Users className="h-10 w-10 text-slate-700 mb-2" />
                  <p className="text-sm text-slate-500">No retailers found</p>
                </div>
              ) : (
                retailers.filter(r => r.has_store).map((r) => (
                  <button
                    key={r.user_id}
                    onClick={() => loadDetail(r)}
                    data-testid={`retailer-item-${r.user_id}`}
                    className={`w-full text-left px-4 py-3 border-b border-slate-800/50 hover:bg-slate-800/40 transition-colors flex items-center gap-3 ${
                      selectedRetailer?.user_id === r.user_id ? 'bg-slate-800/60 border-l-2 border-l-amber-400' : ''
                    }`}
                  >
                    <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                      <span className="text-sm font-bold text-blue-400">{r.name?.[0]?.toUpperCase()}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{r.store_name}</p>
                      <p className="text-xs text-slate-500 truncate">{r.email}</p>
                    </div>
                    <div className="flex flex-col items-end gap-1 flex-shrink-0">
                      <StatusBadge status={r.subscription_status} />
                      <span className="text-[10px] text-slate-600">{r.subscription_tier}</span>
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-600 flex-shrink-0" />
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Detail panel */}
          <div className={`flex-1 ${!selectedRetailer ? 'hidden lg:flex' : 'flex'} flex-col`}>
            {selectedRetailer && detail ? (
              <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-y-auto flex-1">
                {/* Header */}
                <div className="p-6 border-b border-slate-800">
                  <div className="flex items-center gap-3 mb-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => { setSelectedRetailer(null); setDetail(null); }}
                      className="lg:hidden text-slate-400"
                      data-testid="detail-back-btn"
                    >
                      <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                      <Store className="h-6 w-6 text-blue-400" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-white" data-testid="detail-store-name">{detail.store?.store_name}</h2>
                      <p className="text-sm text-slate-400">{detail.store?.subdomain}.shopswift.in</p>
                    </div>
                    <div className="ml-auto">
                      <StatusBadge status={detail.store?.subscription_status} />
                    </div>
                  </div>

                  {/* Contact info */}
                  <div className="flex flex-wrap gap-4 text-sm">
                    <span className="flex items-center gap-1.5 text-slate-400">
                      <Mail className="h-3.5 w-3.5" /> {detail.user?.email}
                    </span>
                    {detail.user?.phone && (
                      <span className="flex items-center gap-1.5 text-slate-400">
                        <Phone className="h-3.5 w-3.5" /> {detail.user.phone}
                      </span>
                    )}
                    {detail.store?.ondc_enabled && (
                      <span className="flex items-center gap-1.5 text-emerald-400">
                        <Globe className="h-3.5 w-3.5" /> ONDC Enabled
                      </span>
                    )}
                  </div>
                </div>

                {/* Stats row */}
                <div className="grid grid-cols-3 gap-4 p-6 border-b border-slate-800">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">{detail.product_count}</p>
                    <p className="text-xs text-slate-500 flex items-center justify-center gap-1"><Package className="h-3 w-3" /> Products</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">{detail.order_count}</p>
                    <p className="text-xs text-slate-500 flex items-center justify-center gap-1"><ShoppingCart className="h-3 w-3" /> Orders</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">₹{(detail.total_revenue || 0).toLocaleString('en-IN')}</p>
                    <p className="text-xs text-slate-500">Revenue</p>
                  </div>
                </div>

                {/* Subscription details */}
                <div className="p-6 border-b border-slate-800">
                  <h3 className="text-sm font-semibold text-slate-300 mb-3">Subscription</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-500 mb-1">Status</p>
                      <StatusBadge status={detail.store?.subscription_status} />
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-500 mb-1">Tier</p>
                      <p className="text-sm font-medium text-white capitalize">{detail.store?.subscription_tier}</p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-500 mb-1">Category</p>
                      <p className="text-sm font-medium text-white capitalize">{detail.store?.category}</p>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <p className="text-xs text-slate-500 mb-1">Template</p>
                      <p className="text-sm font-medium text-white">{detail.store?.template_id}</p>
                    </div>
                  </div>
                </div>

                {/* Recent orders */}
                <div className="p-6">
                  <h3 className="text-sm font-semibold text-slate-300 mb-3">Recent Orders</h3>
                  {detail.recent_orders?.length > 0 ? (
                    <div className="space-y-2">
                      {detail.recent_orders.slice(0, 5).map((o) => (
                        <div key={o.order_id} className="flex items-center justify-between bg-slate-800/30 rounded-lg px-3 py-2">
                          <div>
                            <p className="text-sm text-white">{o.customer_name}</p>
                            <p className="text-xs text-slate-500">{o.order_id}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-white">₹{o.total_amount?.toLocaleString('en-IN')}</p>
                            <StatusBadge status={o.status} />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-600 text-center py-3">No orders yet</p>
                  )}
                </div>
              </div>
            ) : detailLoading ? (
              <div className="flex-1 flex items-center justify-center bg-slate-900 border border-slate-800 rounded-xl">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400" />
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center bg-slate-900 border border-slate-800 rounded-xl">
                <Users className="h-12 w-12 text-slate-700 mb-3" />
                <p className="text-slate-500 text-sm">Select a retailer to view details</p>
              </div>
            )}
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
    cancelled: 'bg-slate-600/20 text-slate-400',
    pending: 'bg-yellow-500/10 text-yellow-400',
    confirmed: 'bg-blue-500/10 text-blue-400',
    delivered: 'bg-emerald-500/10 text-emerald-400',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium inline-block ${styles[status] || 'bg-slate-600/20 text-slate-400'}`}>
      {status || 'none'}
    </span>
  );
}
