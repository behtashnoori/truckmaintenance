import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Header } from '@/components/Header';
import { Button } from '@/components/ui/button';
import { api, Provider, ServiceCategory } from '@/lib/api';
import { Phone, MapPin, LoaderCircle, Truck, Settings, AlertTriangle } from 'lucide-react';

const categoryIcons = {
  roadside: Truck,
  tire: Settings,
  recovery: AlertTriangle,
};

const categoryNames = {
  roadside: 'خدمات جاده‌ای',
  tire: 'لاستیک و رینگ',
  recovery: 'امداد و حادثه',
};

export const ProviderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [provider, setProvider] = useState<Provider | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    fetchProvider();
  }, [id]);

  const fetchProvider = async () => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);

    const response = await api.getProvider(id);
    
    if (response.success && response.data) {
      setProvider(response.data);
    } else {
      setError(response.error || 'خطا در بارگذاری اطلاعات');
    }
    
    setIsLoading(false);
  };

  const handleCall = () => {
    if (provider?.phone) {
      window.location.href = `tel:${provider.phone}`;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title="جزئیات ارائه‌دهنده" />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <LoaderCircle className="animate-spin mx-auto mb-4" size={32} />
            <p className="text-muted-foreground">در حال بارگذاری...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !provider) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title="خطا" />
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <p className="text-destructive mb-4">{error || 'ارائه‌دهنده یافت نشد'}</p>
            <Button onClick={fetchProvider} variant="outline">
              تلاش مجدد
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header title={provider.name} />
      
      <div className="flex-1 p-4 space-y-6">
        {/* Provider Info Card */}
        <div className="bg-card p-6 rounded-lg shadow-card">
          <h1 className="text-xl font-bold mb-4">{provider.name}</h1>
          
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <MapPin size={20} className="text-primary mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-mobile-base">{provider.address}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  فاصله: {provider.distance_km.toFixed(1)} کیلومتر
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Phone size={20} className="text-primary flex-shrink-0" />
              <p className="text-mobile-base ltr">{provider.phone}</p>
            </div>
          </div>
        </div>

        {/* Services */}
        <div className="bg-card p-6 rounded-lg shadow-card">
          <h2 className="text-lg font-semibold mb-4">خدمات ارائه شده</h2>
          
          <div className="grid gap-3">
            {provider.categories.map((category) => {
              const Icon = categoryIcons[category];
              return (
                <div
                  key={category}
                  className="flex items-center gap-3 p-3 bg-muted rounded-lg"
                >
                  <Icon size={24} className="text-primary" />
                  <span className="text-mobile-base">{categoryNames[category]}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Service Area */}
        <div className="bg-card p-6 rounded-lg shadow-card">
          <h2 className="text-lg font-semibold mb-4">محدوده خدمات‌رسانی</h2>
          <div className="flex items-center gap-3">
            <MapPin size={20} className="text-primary" />
            <span className="text-mobile-base">
              شعاع {provider.radius_km} کیلومتری
            </span>
          </div>
        </div>

        {/* Map Placeholder */}
        <div className="bg-muted p-8 rounded-lg text-center">
          <MapPin size={48} className="mx-auto mb-4 text-muted-foreground" />
          <p className="text-muted-foreground">نقشه موقعیت</p>
          <p className="text-sm text-muted-foreground mt-2">
            عرض: {provider.location.lat.toFixed(4)} | طول: {provider.location.lon.toFixed(4)}
          </p>
        </div>

        {/* Call Button */}
        <div className="sticky bottom-4">
          <Button
            onClick={handleCall}
            className="w-full"
            size="lg"
            variant="hero"
          >
            <Phone className="ml-2" size={20} />
            تماس با {provider.name}
          </Button>
        </div>
      </div>
    </div>
  );
};