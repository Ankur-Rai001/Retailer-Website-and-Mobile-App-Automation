import { useState, useEffect } from 'react';
import { Download, X } from 'lucide-react';
import { Button } from './ui/button';
import { isPWA } from '../utils/pwa';

export default function PWAInstallPrompt() {
  const [showPrompt, setShowPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState(null);

  useEffect(() => {
    // Don't show if already installed
    if (isPWA()) {
      return;
    }

    // Check if user dismissed before
    const dismissed = localStorage.getItem('pwa-prompt-dismissed');
    if (dismissed && Date.now() - parseInt(dismissed) < 7 * 24 * 60 * 60 * 1000) {
      return; // Don't show for 7 days after dismissal
    }

    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Show prompt after 10 seconds
      setTimeout(() => {
        setShowPrompt(true);
      }, 10000);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    console.log(`User response: ${outcome}`);
    setDeferredPrompt(null);
    setShowPrompt(false);

    if (outcome === 'accepted') {
      localStorage.removeItem('pwa-prompt-dismissed');
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
  };

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-20 left-4 right-4 md:left-auto md:right-4 md:w-96 bg-white border-2 border-primary rounded-2xl shadow-2xl z-50 animate-in slide-in-from-bottom-5">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
              <Download className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="font-bold text-secondary">Install ShopSwift</h3>
              <p className="text-sm text-muted">Access faster & offline</p>
            </div>
          </div>
          <button
            onClick={handleDismiss}
            className="text-muted hover:text-secondary transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <p className="text-sm text-slate-600 mb-4">
          Install our app for faster access, offline product viewing, and instant notifications.
        </p>

        <div className="flex gap-2">
          <Button
            onClick={handleInstall}
            className="flex-1 bg-primary text-white hover:bg-primary/90 rounded-full"
          >
            Install App
          </Button>
          <Button
            onClick={handleDismiss}
            variant="ghost"
            className="text-muted"
          >
            Not Now
          </Button>
        </div>
      </div>
    </div>
  );
}
