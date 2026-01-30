import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Smartphone, Download, ArrowLeft, CheckCircle, AlertCircle, Loader2, FileCode, Package } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function MobileApp() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [appStatus, setAppStatus] = useState(null);
  const [store, setStore] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const demoToken = localStorage.getItem('demo_session_token');
      const config = {
        withCredentials: true,
        ...(demoToken && { headers: { 'Authorization': `Bearer ${demoToken}` } })
      };

      const [storeRes, appStatusRes] = await Promise.all([
        axios.get(`${API}/stores/my-store`, config),
        axios.get(`${API}/mobile-app/status`, config)
      ]);

      setStore(storeRes.data);
      setAppStatus(appStatusRes.data);
    } catch (error) {
      toast.error('Failed to load mobile app status');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateApp = async () => {
    setGenerating(true);
    try {
      const demoToken = localStorage.getItem('demo_session_token');
      const config = {
        withCredentials: true,
        responseType: 'blob',
        ...(demoToken && { headers: { 'Authorization': `Bearer ${demoToken}` } })
      };

      const response = await axios.post(`${API}/mobile-app/generate`, {}, config);
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${store.store_name.replace(/ /g, '_')}_app.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Mobile app generated! Download started.');
      
      // Refresh status
      await fetchData();
    } catch (error) {
      console.error('App generation error:', error);
      toast.error('Failed to generate mobile app');
    } finally {
      setGenerating(false);
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
            <h1 className="text-2xl font-bold text-secondary">Mobile App Generator</h1>
          </div>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20 rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-6">
            <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center flex-shrink-0">
              <Smartphone className="h-8 w-8 text-primary" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-secondary mb-2">
                Generate Your Branded Mobile App
              </h2>
              <p className="text-slate-600 mb-4">
                Get a fully functional Flutter-based mobile app for Android & iOS with your store branding. 
                We'll publish it under ShopSwift India's centralized developer account.
              </p>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle className="h-4 w-4 text-accent" />
                  <span>Full Flutter source code</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle className="h-4 w-4 text-accent" />
                  <span>APK/IPA build ready</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle className="h-4 w-4 text-accent" />
                  <span>Publishing guide included</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* App Details */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-secondary mb-4">Your App Details</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted">App Name</p>
                <p className="text-base font-semibold text-secondary">{appStatus?.app_name}</p>
              </div>
              <div>
                <p className="text-sm text-muted">Package Name</p>
                <p className="text-sm font-mono text-secondary">{appStatus?.package_name}</p>
              </div>
              <div>
                <p className="text-sm text-muted">Store URL</p>
                <p className="text-sm font-mono text-primary">{store?.subdomain}.shopswift.in</p>
              </div>
              {appStatus?.has_app && (
                <div>
                  <p className="text-sm text-muted">Last Generated</p>
                  <p className="text-sm text-secondary">
                    {new Date(appStatus.app_data.generated_at).toLocaleDateString('en-IN')}
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-secondary mb-4">What You'll Get</h3>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <FileCode className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-secondary">Flutter Source Code</p>
                  <p className="text-sm text-muted">Complete project ready to build</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Package className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-secondary">Build Instructions</p>
                  <p className="text-sm text-muted">Step-by-step APK/IPA generation</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Download className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-secondary">Publishing Guide</p>
                  <p className="text-sm text-muted">Google Play & App Store submission</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Generation Button */}
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
          {appStatus?.has_app ? (
            <div className="mb-6">
              <div className="inline-flex items-center gap-2 bg-accent/10 text-accent px-4 py-2 rounded-full mb-4">
                <CheckCircle className="h-4 w-4" />
                <span className="text-sm font-medium">App Already Generated</span>
              </div>
              <p className="text-sm text-muted">
                You can generate a new version with updated store details
              </p>
            </div>
          ) : (
            <div className="mb-6">
              <AlertCircle className="h-12 w-12 text-orange-500 mx-auto mb-4" />
              <p className="text-muted">
                No mobile app generated yet. Click below to create your app.
              </p>
            </div>
          )}

          <Button
            onClick={handleGenerateApp}
            disabled={generating}
            data-testid="generate-app-button"
            className="bg-primary text-white hover:bg-primary/90 rounded-full px-8 py-6 text-lg font-semibold inline-flex items-center gap-3"
          >
            {generating ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Generating App...
              </>
            ) : (
              <>
                <Download className="h-5 w-5" />
                {appStatus?.has_app ? 'Regenerate Mobile App' : 'Generate Mobile App'}
              </>
            )}
          </Button>

          <p className="text-xs text-muted mt-4">
            Download includes Flutter code, build instructions, and publishing guide
          </p>
        </div>

        {/* Publishing Info */}
        <div className="mt-8 bg-gradient-to-r from-secondary to-slate-800 text-white rounded-xl p-8">
          <h3 className="text-xl font-bold mb-4">Centralized Publishing</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold">📱</span>
                </div>
                <h4 className="font-semibold">Google Play Store</h4>
              </div>
              <p className="text-sm text-slate-300 mb-2">
                Published under <strong>ShopSwift India</strong> developer account
              </p>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• One-time $25 fee (covered by us)</li>
                <li>• Your app name preserved</li>
                <li>• 3-10 days publication time</li>
              </ul>
            </div>

            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold">🍎</span>
                </div>
                <h4 className="font-semibold">Apple App Store</h4>
              </div>
              <p className="text-sm text-slate-300 mb-2">
                Published under <strong>ShopSwift India</strong> developer account
              </p>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• Annual $99 fee (covered by us)</li>
                <li>• Your app name preserved</li>
                <li>• 2-5 days publication time</li>
              </ul>
            </div>
          </div>

          <div className="mt-6 bg-white/10 rounded-lg p-4">
            <p className="text-sm">
              <strong>📧 Submit your app:</strong> Send APK/IPA + screenshots to{' '}
              <span className="font-mono bg-white/20 px-2 py-1 rounded">apps@shopswift.in</span>
            </p>
          </div>
        </div>

        {/* Features Included */}
        <div className="mt-8 bg-white border border-slate-200 rounded-xl p-8">
          <h3 className="text-xl font-bold text-secondary mb-6">App Features Included</h3>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              'Product catalog with images',
              'Category filtering',
              'Product search',
              'Product details page',
              'Shopping cart',
              'Order placement',
              'Store contact info',
              'Push notifications (ready)',
              'Offline product viewing',
              'Fast image loading',
              'Material Design UI',
              'Your store branding',
            ].map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-accent flex-shrink-0" />
                <span className="text-sm text-slate-600">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
