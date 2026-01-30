import { Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function OfflineBanner() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 bg-orange-500 text-white py-2 px-4 z-50 flex items-center justify-center gap-2 shadow-lg">
      <WifiOff className="h-4 w-4" />
      <span className="text-sm font-medium">You are offline - Viewing cached data</span>
      <AlertCircle className="h-4 w-4" />
    </div>
  );
}
