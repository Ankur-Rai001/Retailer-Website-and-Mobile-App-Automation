import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Network, ArrowLeft, CheckCircle, AlertCircle, Loader2, Upload, RefreshCw, FileText, CreditCard } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ONDCIntegration() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [store, setStore] = useState(null);
  const [kycStatus, setKycStatus] = useState(null);
  const [syncStatus, setSyncStatus] = useState(null);
  const [kycForm, setKycForm] = useState({
    gstin: '',
    pan: '',
    bank_account: '',
    bank_ifsc: '',
    bank_name: '',
    account_holder_name: ''
  });

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

      const [storeRes, kycRes, syncRes] = await Promise.all([
        axios.get(`${API}/stores/my-store`, config),
        axios.get(`${API}/ondc/kyc-status`, config),
        axios.get(`${API}/ondc/sync-status`, config)
      ]);

      setStore(storeRes.data);
      setKycStatus(kycRes.data);
      setSyncStatus(syncRes.data);

      // Pre-fill form if KYC exists
      if (kycRes.data.kyc_data) {
        setKycForm({
          gstin: kycRes.data.kyc_data.gstin || '',
          pan: kycRes.data.kyc_data.pan || '',
          bank_account: kycRes.data.kyc_data.bank_account || '',
          bank_ifsc: kycRes.data.kyc_data.bank_ifsc || '',
          bank_name: kycRes.data.kyc_data.bank_name || '',
          account_holder_name: kycRes.data.kyc_data.account_holder_name || ''
        });
      }
    } catch (error) {
      toast.error('Failed to load ONDC status');
    } finally {
      setLoading(false);
    }
  };

  const handleKYCSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const demoToken = localStorage.getItem('demo_session_token');
      const config = {
        withCredentials: true,
        ...(demoToken && { headers: { 'Authorization': `Bearer ${demoToken}` } })
      };

      await axios.post(`${API}/ondc/kyc`, kycForm, config);
      toast.success('KYC submitted successfully! Verification pending.');
      await fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit KYC');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSyncCatalog = async () => {
    setSyncing(true);

    try {
      const demoToken = localStorage.getItem('demo_session_token');
      const config = {
        withCredentials: true,
        ...(demoToken && { headers: { 'Authorization': `Bearer ${demoToken}` } })
      };

      const response = await axios.post(`${API}/ondc/sync-catalog`, {}, config);
      toast.success(`Catalog synced! ${response.data.product_count} products synced to ONDC.`);
      await fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to sync catalog');
    } finally {
      setSyncing(false);
    }
  };

  const handleToggleONDC = async (enabled) => {
    try {
      const demoToken = localStorage.getItem('demo_session_token');
      const config = {
        withCredentials: true,
        ...(demoToken && { headers: { 'Authorization': `Bearer ${demoToken}` } })
      };

      await axios.patch(`${API}/stores/${store.store_id}`, { ondc_enabled: enabled }, config);
      setStore({ ...store, ondc_enabled: enabled });
      toast.success(enabled ? 'ONDC enabled!' : 'ONDC disabled');
    } catch (error) {
      toast.error('Failed to update ONDC status');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const kycVerified = kycStatus?.kyc_data?.status === 'verified';
  const kycPending = kycStatus?.kyc_data?.status === 'pending';
  const kycNotSubmitted = !kycStatus?.has_kyc;

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/settings')}
              data-testid="back-button"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-2xl font-bold text-secondary">ONDC Integration</h1>
          </div>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-2xl p-8 mb-8">
          <div className="flex items-start gap-6">
            <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <Network className="h-8 w-8 text-blue-600" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-secondary mb-2">
                Join ONDC Network
              </h2>
              <p className="text-slate-600 mb-4">
                List your products on India's Open Network for Digital Commerce. 
                Reach customers on PhonePe, Paytm, Google Pay, and other buyer apps.
              </p>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle className="h-4 w-4 text-accent" />
                  <span>Zero listing fees</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle className="h-4 w-4 text-accent" />
                  <span>Multi-app reach</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <CheckCircle className="h-4 w-4 text-accent" />
                  <span>Auto order sync</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ONDC Enable Toggle */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-secondary">ONDC Integration Status</h3>
              <p className="text-sm text-muted">
                {store?.ondc_enabled ? 'Your store is listed on ONDC' : 'Enable to start listing on ONDC'}
              </p>
            </div>
            <Switch
              checked={store?.ondc_enabled || false}
              onCheckedChange={handleToggleONDC}
              disabled={!kycVerified}
              data-testid="ondc-toggle"
            />
          </div>
          {!kycVerified && (
            <div className="mt-4 bg-orange-50 border border-orange-200 rounded-lg p-4">
              <p className="text-sm text-orange-800">
                ⚠️ Complete KYC verification below to enable ONDC integration
              </p>
            </div>
          )}
        </div>

        {/* KYC Status */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-secondary">KYC Verification</h3>
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${
              kycVerified ? 'bg-green-100 text-green-700' :
              kycPending ? 'bg-orange-100 text-orange-700' :
              'bg-slate-100 text-slate-700'
            }`}>
              {kycVerified && <CheckCircle className="h-4 w-4" />}
              {kycPending && <Loader2 className="h-4 w-4 animate-spin" />}
              {kycNotSubmitted && <AlertCircle className="h-4 w-4" />}
              <span>
                {kycVerified ? 'Verified' :
                 kycPending ? 'Pending Review' :
                 'Not Submitted'}
              </span>
            </div>
          </div>

          {kycVerified ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800 mb-2">
                ✓ Your KYC is verified! You can now sync your catalog to ONDC.
              </p>
              <div className="grid md:grid-cols-2 gap-2 text-xs text-green-700">
                <div>GSTIN: {kycStatus.kyc_data.gstin}</div>
                <div>PAN: {kycStatus.kyc_data.pan}</div>
                <div>Bank: {kycStatus.kyc_data.bank_name}</div>
                <div>IFSC: {kycStatus.kyc_data.bank_ifsc}</div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleKYCSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="gstin">GSTIN *</Label>
                  <Input
                    id="gstin"
                    data-testid="gstin-input"
                    placeholder="22AAAAA0000A1Z5"
                    value={kycForm.gstin}
                    onChange={(e) => setKycForm({ ...kycForm, gstin: e.target.value })}
                    className="h-12"
                    required
                    disabled={kycPending}
                  />
                </div>
                <div>
                  <Label htmlFor="pan">PAN Card *</Label>
                  <Input
                    id="pan"
                    data-testid="pan-input"
                    placeholder="ABCDE1234F"
                    value={kycForm.pan}
                    onChange={(e) => setKycForm({ ...kycForm, pan: e.target.value.toUpperCase() })}
                    className="h-12"
                    required
                    disabled={kycPending}
                    maxLength={10}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="account_holder">Account Holder Name *</Label>
                <Input
                  id="account_holder"
                  data-testid="account-holder-input"
                  placeholder="As per bank records"
                  value={kycForm.account_holder_name}
                  onChange={(e) => setKycForm({ ...kycForm, account_holder_name: e.target.value })}
                  className="h-12"
                  required
                  disabled={kycPending}
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="bank_account">Bank Account Number *</Label>
                  <Input
                    id="bank_account"
                    data-testid="bank-account-input"
                    placeholder="1234567890"
                    value={kycForm.bank_account}
                    onChange={(e) => setKycForm({ ...kycForm, bank_account: e.target.value })}
                    className="h-12"
                    required
                    disabled={kycPending}
                  />
                </div>
                <div>
                  <Label htmlFor="bank_ifsc">IFSC Code *</Label>
                  <Input
                    id="bank_ifsc"
                    data-testid="bank-ifsc-input"
                    placeholder="SBIN0001234"
                    value={kycForm.bank_ifsc}
                    onChange={(e) => setKycForm({ ...kycForm, bank_ifsc: e.target.value.toUpperCase() })}
                    className="h-12"
                    required
                    disabled={kycPending}
                    maxLength={11}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="bank_name">Bank Name *</Label>
                <Input
                  id="bank_name"
                  data-testid="bank-name-input"
                  placeholder="State Bank of India"
                  value={kycForm.bank_name}
                  onChange={(e) => setKycForm({ ...kycForm, bank_name: e.target.value })}
                  className="h-12"
                  required
                  disabled={kycPending}
                />
              </div>

              <Button
                type="submit"
                disabled={submitting || kycPending}
                data-testid="submit-kyc-button"
                className="w-full bg-primary text-white hover:bg-primary/90 rounded-full py-6 font-semibold"
              >
                {submitting ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Submitting KYC...
                  </>
                ) : kycPending ? (
                  'KYC Under Review'
                ) : (
                  <>
                    <FileText className="mr-2 h-5 w-5" />
                    Submit KYC for Verification
                  </>
                )}
              </Button>
            </form>
          )}
        </div>

        {/* Catalog Sync */}
        {kycVerified && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-secondary">Catalog Sync</h3>
                <p className="text-sm text-muted">
                  Sync your products to ONDC network
                </p>
              </div>
              {syncStatus?.last_sync && (
                <div className="text-right">
                  <p className="text-xs text-muted">Last synced</p>
                  <p className="text-sm font-medium text-secondary">
                    {new Date(syncStatus.last_sync.synced_at).toLocaleString('en-IN')}
                  </p>
                  <p className="text-xs text-muted">
                    {syncStatus.last_sync.product_count} products
                  </p>
                </div>
              )}
            </div>

            <Button
              onClick={handleSyncCatalog}
              disabled={syncing || !store?.ondc_enabled}
              data-testid="sync-catalog-button"
              className="w-full bg-accent text-white hover:bg-accent/90 rounded-full py-6 font-semibold"
            >
              {syncing ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Syncing Catalog...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-5 w-5" />
                  {syncStatus?.has_synced ? 'Re-sync Catalog' : 'Sync Catalog to ONDC'}
                </>
              )}
            </Button>

            {!store?.ondc_enabled && (
              <p className="text-xs text-center text-muted mt-2">
                Enable ONDC integration above to sync catalog
              </p>
            )}
          </div>
        )}

        {/* Information Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-secondary mb-4">How ONDC Works</h3>
            <ul className="space-y-3 text-sm text-slate-600">
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">1.</span>
                <span>Complete KYC with GSTIN, PAN, and bank details</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">2.</span>
                <span>Sync your product catalog to ONDC network</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">3.</span>
                <span>Customers discover you on PhonePe, Paytm, etc.</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">4.</span>
                <span>Orders automatically appear in your dashboard</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">5.</span>
                <span>Get paid directly to your bank account</span>
              </li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-secondary mb-4">Benefits</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-accent flex-shrink-0" />
                <span>Reach millions of customers across India</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-accent flex-shrink-0" />
                <span>Zero listing or commission fees</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-accent flex-shrink-0" />
                <span>Multi-app visibility (PhonePe, Paytm, etc.)</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-accent flex-shrink-0" />
                <span>Automatic order and payment management</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-accent flex-shrink-0" />
                <span>Government-backed digital commerce</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
