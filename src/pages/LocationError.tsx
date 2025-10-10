import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { PageNavigation } from '@/components/PageNavigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useLocation } from '@/contexts/LocationContext';
import { MapPin, AlertCircle } from 'lucide-react';

export const LocationError: React.FC = () => {
  const navigate = useNavigate();
  const { requestLocation, setManualLocation, clearError } = useLocation();
  const [manualLat, setManualLat] = useState('');
  const [manualLon, setManualLon] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRetry = () => {
    clearError();
    requestLocation();
  };

  const handleManualSubmit = async () => {
    const lat = parseFloat(manualLat);
    const lon = parseFloat(manualLon);

    if (isNaN(lat) || isNaN(lon)) {
      alert('لطفاً مختصات معتبر وارد کنید');
      return;
    }

    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      alert('مختصات وارد شده خارج از محدوده مجاز است');
      return;
    }

    setIsSubmitting(true);
    setManualLocation(lat, lon);
    
    // Small delay for better UX
    await new Promise(resolve => setTimeout(resolve, 500));
    
    setIsSubmitting(false);
    navigate('/services');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="خطای موقعیت" showBack={false} />
      
      <div className="flex-1 p-6 space-y-6">
        {/* Error Icon */}
        <div className="text-center py-8">
          <AlertCircle size={64} className="mx-auto mb-4 text-destructive" />
          <h1 className="text-xl font-bold mb-2">دسترسی به موقعیت محدود شده</h1>
          <p className="text-muted-foreground">
            برای یافتن بهترین خدمات نزدیک شما، به موقعیت جغرافیایی نیاز داریم
          </p>
        </div>

        {/* Why Location is Needed */}
        <div className="bg-card p-4 rounded-lg shadow-card">
          <h2 className="font-semibold mb-2">چرا موقعیت لازم است؟</h2>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• یافتن نزدیک‌ترین ارائه‌دهندگان خدمات</li>
            <li>• محاسبه دقیق فاصله و زمان رسیدن</li>
            <li>• ارائه بهترین پیشنهادات بر اساس منطقه شما</li>
          </ul>
        </div>

        {/* Retry Button */}
        <Button
          onClick={handleRetry}
          className="w-full"
          size="lg"
          variant="default"
        >
          <MapPin className="ml-2" size={20} />
          تلاش مجدد برای دریافت موقعیت
        </Button>

        {/* Manual Input */}
        <div className="bg-card p-4 rounded-lg shadow-card">
          <h2 className="font-semibold mb-4">وارد کردن دستی مختصات</h2>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="lat">عرض جغرافیایی (Latitude)</Label>
              <Input
                id="lat"
                type="number"
                step="any"
                placeholder="مثال: 35.7219"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                className="ltr text-right"
              />
            </div>
            
            <div>
              <Label htmlFor="lon">طول جغرافیایی (Longitude)</Label>
              <Input
                id="lon"
                type="number"
                step="any"
                placeholder="مثال: 51.3347"
                value={manualLon}
                onChange={(e) => setManualLon(e.target.value)}
                className="ltr text-right"
              />
            </div>
            
            <Button
              onClick={handleManualSubmit}
              disabled={!manualLat || !manualLon || isSubmitting}
              className="w-full"
              variant="outline"
            >
              {isSubmitting ? 'در حال تنظیم...' : 'تنظیم موقعیت'}
            </Button>
          </div>
        </div>

        {/* Help Text */}
        <div className="text-center text-sm text-muted-foreground">
          <p>
            برای یافتن مختصات خود می‌توانید از سرویس‌های نقشه آنلاین استفاده کنید
          </p>
        </div>
        
        {/* Navigation */}
        <PageNavigation position="bottom" variant="floating" />
      </div>
    </div>
  );
};