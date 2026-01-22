import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Store, ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function StoreSetup() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    store_name: '',
    category: '',
    language: 'en',
    phone: '',
    address: '',
    gst_number: ''
  });

  const categories = [
    { value: 'grocery', label: 'Grocery & Kirana Store' },
    { value: 'clothing', label: 'Clothing & Fashion' },
    { value: 'electronics', label: 'Electronics' },
    { value: 'pharmacy', label: 'Pharmacy & Medical' },
    { value: 'restaurant', label: 'Restaurant & Food' },
    { value: 'jewelry', label: 'Jewelry & Accessories' },
    { value: 'books', label: 'Books & Stationery' },
    { value: 'hardware', label: 'Hardware & Tools' },
    { value: 'general', label: 'General Store' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.store_name || !formData.category) {
      toast.error('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/stores`,
        formData,
        { withCredentials: true }
      );
      
      toast.success(`${response.data.store_name} created successfully! \ud83c\udf89`);
      navigate('/dashboard');
    } catch (error) {
      console.error('Store creation error:', error);
      toast.error(error.response?.data?.detail || 'Failed to create store');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-accent/5 flex items-center justify-center px-6 py-12">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <div className="inline-block p-4 bg-primary/10 rounded-full mb-4">
            <Store className="h-12 w-12 text-primary" />
          </div>
          <h1 className="text-4xl font-bold text-secondary mb-2">Create Your Store</h1>
          <p className="text-lg text-slate-600">Let AI help you set up your online store in minutes</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl p-8 shadow-lg">
          <div className="space-y-6">
            <div>
              <Label htmlFor="store_name" className="text-sm font-semibold text-secondary mb-2 block">
                Store Name *
              </Label>
              <Input
                id="store_name"
                data-testid="store-name-input"
                placeholder="e.g., Ram Kirana Store"
                value={formData.store_name}
                onChange={(e) => setFormData({ ...formData, store_name: e.target.value })}
                className="h-12 bg-slate-50 border-slate-200 focus:border-primary focus:ring-primary/20 rounded-lg"
                required
              />
            </div>

            <div>
              <Label htmlFor="category" className="text-sm font-semibold text-secondary mb-2 block">
                Store Category *
              </Label>
              <Select 
                value={formData.category} 
                onValueChange={(value) => setFormData({ ...formData, category: value })}
              >
                <SelectTrigger data-testid="category-select" className="h-12 bg-slate-50 border-slate-200 rounded-lg">
                  <SelectValue placeholder="Select your store type" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(cat => (
                    <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="phone" className="text-sm font-semibold text-secondary mb-2 block">
                Phone Number
              </Label>
              <Input
                id="phone"
                data-testid="phone-input"
                type="tel"
                placeholder="+91 98765 43210"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="h-12 bg-slate-50 border-slate-200 focus:border-primary focus:ring-primary/20 rounded-lg"
              />
            </div>

            <div>
              <Label htmlFor="address" className="text-sm font-semibold text-secondary mb-2 block">
                Store Address
              </Label>
              <Input
                id="address"
                data-testid="address-input"
                placeholder="Shop No. 5, Main Market, City"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="h-12 bg-slate-50 border-slate-200 focus:border-primary focus:ring-primary/20 rounded-lg"
              />
            </div>

            <div>
              <Label htmlFor="gst" className="text-sm font-semibold text-secondary mb-2 block">
                GST Number (Optional)
              </Label>
              <Input
                id="gst"
                data-testid="gst-input"
                placeholder="22AAAAA0000A1Z5"
                value={formData.gst_number}
                onChange={(e) => setFormData({ ...formData, gst_number: e.target.value })}
                className="h-12 bg-slate-50 border-slate-200 focus:border-primary focus:ring-primary/20 rounded-lg"
              />
            </div>

            <div>
              <Label htmlFor="language" className="text-sm font-semibold text-secondary mb-2 block">
                Preferred Language
              </Label>
              <Select 
                value={formData.language} 
                onValueChange={(value) => setFormData({ ...formData, language: value })}
              >
                <SelectTrigger className="h-12 bg-slate-50 border-slate-200 rounded-lg">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="hi">Hindi (हिंदी)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button 
            type="submit" 
            data-testid="create-store-button"
            disabled={loading}
            className="w-full mt-8 bg-primary text-white hover:bg-primary/90 rounded-full py-6 text-lg font-semibold shadow-lg transition-all hover:shadow-xl hover:-translate-y-0.5"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Creating Your Store...
              </>
            ) : (
              <>
                Create My Store
                <ArrowRight className="ml-2 h-5 w-5" />
              </>
            )}
          </Button>

          <p className="text-sm text-center text-muted mt-4">
            AI will automatically generate your store description and setup
          </p>
        </form>
      </div>
    </div>
  );
}
