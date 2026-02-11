import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  CreditCard, Users, RefreshCw, Check
} from 'lucide-react';
import { Button } from '../components/ui/button';
import AdminNav from '../components/AdminNav';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TIER_PRICES = { basic: 99, pro: 199, premium: 299 };

export default function AdminSubscriptions() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [retailers, setRetailers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(null);

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

  const fetchRetailers = async () => {
    const res = await axios.get(`${API}/admin/retailers`, { withCredentials: true });
    setRetailers(res.data.filter(r => r.has_store));
  };

  const handleUpdate = async (userId, status, tier) => {
    setUpdating(userId);
    try {
      await axios.patch(
        `${API}/admin/retailers/${userId}/subscription`,
        { subscription_status: status, subscription_tier: tier },
        { withCredentials: true }
      );
      toast.success('Subscription updated');
      await fetchRetailers();
    } catch (err) {
      toast.error('Failed to update subscription');
    } finally {
      setUpdating(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-amber-400" />
      </div>
    );
  }

  const grouped = {
    active: retailers.filter(r => r.subscription_status === 'active'),
    trial: retailers.filter(r => r.subscription_status === 'trial'),
    expired: retailers.filter(r => r.subscription_status === 'expired'),
    cancelled: retailers.filter(r => r.subscription_status === 'cancelled'),
  };

  return (
    <div className="min-h-screen bg-slate-950" data-testid="admin-subscriptions-page">
      <AdminNav user={user} />

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white mb-1">Subscription Management</h1>
            <p className="text-slate-400 text-sm">Manage retailer plans — zero transaction fees</p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchRetailers}
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
            data-testid="refresh-subs-btn"
          >
            <RefreshCw className="h-4 w-4 mr-1" /> Refresh
          </Button>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {Object.entries(grouped).map(([status, list]) => (
            <div key={status} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <p className="text-2xl font-bold text-white">{list.length}</p>
              <p className="text-xs text-slate-500 capitalize mt-1">{status}</p>
            </div>
          ))}
        </div>

        {/* Retailer subscription table */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full" data-testid="subscription-table">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Store</th>
                  <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Status</th>
                  <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Tier</th>
                  <th className="text-left text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Price</th>
                  <th className="text-right text-xs font-medium text-slate-500 uppercase tracking-wider px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {retailers.map((r) => (
                  <tr key={r.user_id} className="border-b border-slate-800/50 hover:bg-slate-800/20" data-testid={`sub-row-${r.user_id}`}>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                          <span className="text-xs font-bold text-blue-400">{r.name?.[0]?.toUpperCase()}</span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">{r.store_name}</p>
                          <p className="text-xs text-slate-500">{r.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={r.subscription_status} />
                    </td>
                    <td className="px-4 py-3">
                      <select
                        value={r.subscription_tier}
                        onChange={(e) => handleUpdate(r.user_id, r.subscription_status, e.target.value)}
                        disabled={updating === r.user_id}
                        className="text-sm bg-slate-800 border border-slate-700 text-slate-300 rounded px-2 py-1"
                        data-testid={`tier-select-${r.user_id}`}
                      >
                        <option value="basic">Basic</option>
                        <option value="pro">Pro</option>
                        <option value="premium">Premium</option>
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-slate-300">₹{TIER_PRICES[r.subscription_tier] || 99}/mo</span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {r.subscription_status !== 'active' && (
                          <Button
                            size="sm"
                            onClick={() => handleUpdate(r.user_id, 'active', r.subscription_tier)}
                            disabled={updating === r.user_id}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs h-7 px-2"
                            data-testid={`activate-btn-${r.user_id}`}
                          >
                            {updating === r.user_id ? <RefreshCw className="h-3 w-3 animate-spin" /> : <Check className="h-3 w-3 mr-1" />}
                            Activate
                          </Button>
                        )}
                        {r.subscription_status === 'active' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleUpdate(r.user_id, 'cancelled', r.subscription_tier)}
                            disabled={updating === r.user_id}
                            className="border-red-800 text-red-400 hover:bg-red-900/30 text-xs h-7 px-2"
                            data-testid={`cancel-btn-${r.user_id}`}
                          >
                            Cancel
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${styles[status] || 'bg-slate-600/20 text-slate-400'}`}>
      {status || 'none'}
    </span>
  );
}
