import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Store, Globe, Palette, Save, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Settings() {
  const navigate = useNavigate();
  const [store, setStore] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    store_name: '',
    description: '',
    phone: '',
    address: '',
    gst_number: '',
    custom_domain: '',
    template_id: '',
    language: 'en',
    ondc_enabled: false
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [storeRes, templatesRes] = await Promise.all([
        axios.get(`${API}/stores/my-store`, { withCredentials: true }),
        axios.get(`${API}/templates`, { withCredentials: true })
      ]);
      
      setStore(storeRes.data);
      setTemplates(templatesRes.data);
      setFormData({
        store_name: storeRes.data.store_name,
        description: storeRes.data.description || '',
        phone: storeRes.data.phone || '',
        address: storeRes.data.address || '',
        gst_number: storeRes.data.gst_number || '',
        custom_domain: storeRes.data.custom_domain || '',
        template_id: storeRes.data.template_id,
        language: storeRes.data.language,
        ondc_enabled: storeRes.data.ondc_enabled
      });
    } catch (error) {
      toast.error('Failed to load settings');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    
    try {
      await axios.patch(
        `${API}/stores/${store.store_id}`,
        formData,
        { withCredentials: true }
      );
      toast.success('Settings saved successfully');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
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
            <h1 className="text-2xl font-bold text-secondary">Store Settings</h1>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="bg-white border border-slate-200 rounded-xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <Store className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold text-secondary">Basic Information</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="store_name">Store Name</Label>
                <Input
                  id="store_name"
                  data-testid="store-name-input"
                  value={formData.store_name}
                  onChange={(e) => setFormData({ ...formData, store_name: e.target.value })}
                  className="h-12"
                />
              </div>

              <div>
                <Label htmlFor="description">Store Description</Label>
                <Input
                  id="description"
                  data-testid="description-input"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="h-12"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phone">Phone Number</Label>
                  <Input
                    id="phone"
                    data-testid="phone-input"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="h-12"
                  />
                </div>
                <div>
                  <Label htmlFor="gst">GST Number</Label>
                  <Input
                    id="gst"
                    data-testid="gst-input"
                    value={formData.gst_number}
                    onChange={(e) => setFormData({ ...formData, gst_number: e.target.value })}
                    className="h-12"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="address">Store Address</Label>
                <Input
                  id="address"
                  data-testid="address-input"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="h-12"
                />
              </div>

              <div>
                <Label htmlFor="language">Preferred Language</Label>
                <Select 
                  value={formData.language} 
                  onValueChange={(value) => setFormData({ ...formData, language: value })}
                >
                  <SelectTrigger className="h-12">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="hi">Hindi (हिंदी)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <Globe className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold text-secondary">Domain Settings</h2>
            </div>

            <div className="space-y-4">
              <div>
                <Label>Default Subdomain</Label>
                <div className="flex items-center gap-2 mt-2">
                  <Input
                    value={store.subdomain}
                    disabled
                    className="h-12 bg-slate-100"
                  />
                  <span className="text-muted">.shopswift.in</span>
                </div>
                <p className="text-xs text-muted mt-1">Your free subdomain (cannot be changed)</p>
              </div>

              <div>
                <Label htmlFor="custom_domain">Custom Domain (Optional)</Label>
                <Input
                  id="custom_domain"
                  data-testid="custom-domain-input"
                  placeholder="www.mystore.com"
                  value={formData.custom_domain}
                  onChange={(e) => setFormData({ ...formData, custom_domain: e.target.value })}
                  className="h-12"
                />
                <p className="text-xs text-muted mt-1">Add your own domain (requires DNS configuration)</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-8">
            <div className="flex items-center gap-3 mb-6">
              <Palette className="h-6 w-6 text-primary" />
              <h2 className="text-xl font-semibold text-secondary">Store Template</h2>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {templates.map((template) => (
                <div
                  key={template.template_id}
                  onClick={() => setFormData({ ...formData, template_id: template.template_id })}
                  className={`border-2 rounded-xl p-4 cursor-pointer transition-all ${
                    formData.template_id === template.template_id
                      ? 'border-primary bg-primary/5'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <img 
                    src={template.preview_url} 
                    alt={template.name}
                    className="w-full h-32 object-cover rounded-lg mb-3"
                  />
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-secondary">{template.name}</h3>
                      <p className="text-xs text-muted">{template.description}</p>
                    </div>
                    {template.is_premium && (
                      <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full font-semibold">
                        ₹{template.price}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-8">
            <h2 className="text-xl font-semibold text-secondary mb-6">Advanced Features</h2>
            
            <div className="flex items-center justify-between py-4 border-b border-slate-100">
              <div>
                <h3 className="font-semibold text-secondary">ONDC Integration</h3>
                <p className="text-sm text-muted">List your products on ONDC network (PhonePe, Paytm, etc.)</p>
              </div>
              <Button
                onClick={() => navigate('/ondc')}
                variant="outline"
                className="border-primary text-primary hover:bg-primary/10"
              >
                Configure ONDC
              </Button>
            </div>
          </div>

          <div className="flex gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              data-testid="save-settings-button"
              disabled={saving}
              className="flex-1 bg-primary text-white hover:bg-primary/90"
            >
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Settings
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
