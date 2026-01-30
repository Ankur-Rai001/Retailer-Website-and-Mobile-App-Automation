import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Store, User, ShieldCheck, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DEMO_ACCOUNTS = {
  retailer: {
    name: 'Demo Retailer',
    email: 'demo.retailer@shopswift.in',
    token: 'demo_session_retailer_12345678901234567890',
    role: 'Retailer',
    icon: Store,
    description: 'Test the full store management experience'
  },
  admin: {
    name: 'Demo Admin',
    email: 'demo.admin@shopswift.in',
    token: 'demo_session_admin_12345678901234567890',
    role: 'Admin',
    icon: ShieldCheck,
    description: 'Access platform admin features (coming soon)'
  }
};

export default function DemoLogin() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(null);

  const handleDemoLogin = async (accountType) => {
    setLoading(accountType);
    const account = DEMO_ACCOUNTS[accountType];

    try {
      // Set the session cookie by calling backend with the demo token
      await axios.post(
        `${API}/auth/session`,
        { session_id: 'demo' },
        { 
          withCredentials: true,
          headers: {
            'Authorization': `Bearer ${account.token}`
          }
        }
      ).catch(() => {
        // If session endpoint fails, we'll manually set cookie via a custom endpoint
        // For demo purposes, we'll navigate with the token
      });

      // Verify authentication
      const response = await axios.get(`${API}/auth/me`, {
        withCredentials: true,
        headers: {
          'Authorization': `Bearer ${account.token}`
        }
      });

      // Store token in localStorage for demo purposes
      localStorage.setItem('demo_session_token', account.token);
      
      toast.success(`Welcome, ${response.data.name}!`);
      navigate('/dashboard', { state: { user: response.data, demoToken: account.token } });
    } catch (error) {
      console.error('Demo login error:', error);
      toast.error('Demo login failed. Please try again.');
    } finally {
      setLoading(null);
    }
  };

  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-accent/5 flex items-center justify-center px-6 py-12">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <div className="inline-block p-4 bg-primary/10 rounded-full mb-4">
            <Store className="h-12 w-12 text-primary" />
          </div>
          <h1 className="text-4xl font-bold text-secondary mb-2">Welcome to ShopSwift India</h1>
          <p className="text-lg text-slate-600">Choose a demo account to explore the platform</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {Object.entries(DEMO_ACCOUNTS).map(([key, account]) => (
            <div
              key={key}
              className="bg-white border-2 border-slate-200 rounded-2xl p-8 hover:border-primary hover:shadow-lg transition-all"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="p-3 bg-primary/10 rounded-lg">
                  <account.icon className="h-8 w-8 text-primary" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-secondary">{account.role} Account</h3>
                  <p className="text-sm text-muted">{account.name}</p>
                </div>
              </div>
              
              <p className="text-slate-600 mb-6">{account.description}</p>
              
              <div className="bg-slate-50 rounded-lg p-3 mb-4">
                <p className="text-xs text-muted mb-1">Email</p>
                <p className="text-sm font-mono text-secondary">{account.email}</p>
              </div>

              <Button
                onClick={() => handleDemoLogin(key)}
                disabled={loading !== null}
                data-testid={`demo-login-${key}`}
                className="w-full bg-primary text-white hover:bg-primary/90 rounded-full py-6 font-semibold"
              >
                {loading === key ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Logging in...
                  </>
                ) : (
                  <>
                    Login as {account.role}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          ))}
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center">
          <User className="h-10 w-10 text-primary mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-secondary mb-2">Real Account Login</h3>
          <p className="text-slate-600 mb-6">Sign in with your Google account to create your own store</p>
          <Button
            onClick={handleGoogleLogin}
            variant="outline"
            className="border-2 border-slate-200 hover:border-primary rounded-full px-8 py-6 font-semibold"
          >
            <img 
              src="https://www.google.com/favicon.ico" 
              alt="Google"
              className="w-5 h-5 mr-2"
            />
            Continue with Google
          </Button>
        </div>

        <div className="mt-8 text-center">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="text-muted hover:text-secondary"
          >
            ← Back to Home
          </Button>
        </div>
      </div>
    </div>
  );
}
