import { Store, Package, ShoppingCart, BarChart3, Settings, LogOut } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from './ui/button';
import axios from 'axios';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function DashboardNav({ user }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`, {}, { withCredentials: true });
      navigate('/');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  const navItems = [
    { path: '/dashboard', icon: Store, label: 'Dashboard' },
    { path: '/products', icon: Package, label: 'Products' },
    { path: '/orders', icon: ShoppingCart, label: 'Orders' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <Store className="h-6 w-6 text-primary" />
              <span className="font-heading text-xl font-bold text-secondary">ShopSwift</span>
            </div>
            
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(item.path)}
                  className={`flex items-center gap-2 ${
                    isActive(item.path) 
                      ? 'text-primary bg-primary/10 font-semibold' 
                      : 'text-muted hover:text-secondary'
                  }`}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-sm text-muted hidden sm:block">{user?.name}</span>
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
  );
}
