import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Footer } from '@/components/Footer';
import { useLocation } from '@/contexts/LocationContext';
import { MapPin, Truck } from 'lucide-react';

export const SearchPage: React.FC = () => {
  const { lat, lon, isLoading, error, requestLocation } = useLocation();
  const navigate = useNavigate();

  const hasLocation = lat && lon;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <div className="gradient-hero text-white p-6 text-center">
        <div className="max-w-md mx-auto">
          <Truck size={48} className="mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">امداد کامیون</h1>
          <p className="opacity-90">خدمات اضطراری و تعمیرات سنگین</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 space-y-6">
        {/* Location Status */}
        <div className="bg-card p-4 rounded-lg shadow-card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin size={20} className="text-primary" />
              <span className="text-mobile-base">
                {isLoading ? 'در حال یافتن موقعیت...' : 
                 hasLocation ? 'موقعیت شما تأیید شد' : 
                 'موقعیت مورد نیاز'}
              </span>
            </div>
            {!hasLocation && !isLoading && (
              <Button variant="outline" size="sm" onClick={requestLocation}>
                تأیید موقعیت
              </Button>
            )}
          </div>
          
          {error && (
            <div className="mt-2 text-sm text-destructive">
              {error}
            </div>
          )}
        </div>

        {/* Provider Registration Link */}
        <div className="text-center pt-4">
          <p className="text-sm text-muted-foreground mb-2">
            ارائه‌دهنده خدمات هستید؟
          </p>
          <Button
            variant="outline"
            onClick={() => navigate('/signup')}
            className="w-full"
          >
            ثبت‌نام ارائه‌دهنده
          </Button>
        </div>
      </div>

      <Footer />
    </div>
  );
};