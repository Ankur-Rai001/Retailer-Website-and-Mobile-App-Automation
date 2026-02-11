import { useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, Users, CreditCard, BarChart3, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function AdminNav({ user }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      localStorage.removeItem('demo_session_token');
      navigate('/');
    } catch {
      toast.error('Logout failed');
    }
  };

  const navItems = [
    { path: '/admin', icon: BarChart3, label: 'Overview' },
    { path: '/admin/retailers', icon: Users, label: 'Retailers' },
    { path: '/admin/subscriptions', icon: CreditCard, label: 'Subscriptions' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-slate-900 sticky top-0 z-50" data-testid="admin-nav">
      <div className="max-w-7xl mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-amber-400" />
              <span className="font-heading text-lg font-bold text-white">ShopSwift</span>
              <span className="text-xs bg-amber-400/20 text-amber-400 px-2 py-0.5 rounded-full font-medium">ADMIN</span>
            </div>

            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(item.path)}
                  data-testid={`admin-nav-${item.label.toLowerCase()}`}
                  className={`flex items-center gap-2 text-sm ${
                    isActive(item.path)
                      ? 'text-amber-400 bg-white/10 font-semibold'
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400 hidden sm:block">{user?.name}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              data-testid="admin-logout-button"
              className="text-slate-400 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
