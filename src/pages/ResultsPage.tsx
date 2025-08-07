import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { CategorySelector } from '@/components/CategorySelector';
import { Button } from '@/components/ui/button';
import { api, ProviderSearchResult, ServiceCategory } from '@/lib/api';
import { Phone, MapPin, LoaderCircle } from 'lucide-react';

export const ResultsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [providers, setProviders] = useState<ProviderSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const lat = parseFloat(searchParams.get('lat') || '0');
  const lon = parseFloat(searchParams.get('lon') || '0');
  const category = searchParams.get('category') as ServiceCategory | null;

  useEffect(() => {
    if (!lat || !lon) {
      navigate('/location-error');
      return;
    }

    fetchProviders();
  }, [lat, lon, category]);

  const fetchProviders = async () => {
    setIsLoading(true);
    setError(null);

    const response = await api.searchProviders(lat, lon, category || undefined);
    
    if (response.success && response.data) {
      setProviders(response.data);
    } else {
      setError(response.error || 'خطا در بارگذاری نتایج');
    }
    
    setIsLoading(false);
  };

  const handleCategoryChange = (newCategory: ServiceCategory) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('category', newCategory);
    setSearchParams(newParams);
  };

  const handleCall = (phone: string) => {
    window.location.href = `tel:${phone}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title="جستجوی خدمات" />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <LoaderCircle className="animate-spin mx-auto mb-4" size={32} />
            <p className="text-muted-foreground">در حال جستجو...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="نتایج جستجو" />
      
      {/* Filter Bar */}
      <div className="sticky top-16 z-40 bg-background/95 backdrop-blur-sm border-b p-4">
        <CategorySelector
          selectedCategory={category || undefined}
          onCategorySelect={handleCategoryChange}
          variant="compact"
        />
      </div>

      {/* Results */}
      <div className="flex-1 p-4">
        {error ? (
          <div className="text-center py-8">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={fetchProviders} variant="outline">
              تلاش مجدد
            </Button>
          </div>
        ) : providers.length === 0 ? (
          <div className="text-center py-8">
            <MapPin size={48} className="mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">هیچ خدماتی یافت نشد</h3>
            <p className="text-muted-foreground mb-4">
              در این منطقه ارائه‌دهنده‌ای برای این نوع خدمات یافت نشد
            </p>
            <Button 
              onClick={() => navigate('/')} 
              variant="outline"
            >
              جستجوی جدید
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground mb-4">
              {providers.length} ارائه‌دهنده یافت شد
            </div>
            
            {providers.map((provider) => (
              <div
                key={provider.id}
                className="bg-card p-4 rounded-lg shadow-card border hover:shadow-floating transition-smooth cursor-pointer"
                onClick={() => navigate(`/provider/${provider.id}`)}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-mobile-base mb-1">
                      {provider.name}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      {provider.address}
                    </p>
                    <div className="flex items-center gap-1 text-sm text-primary">
                      <MapPin size={16} />
                      {provider.distance_km.toFixed(1)} کیلومتر
                    </div>
                  </div>
                  
                  <Button
                    variant="secondary"
                    size="icon-sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCall(provider.phone);
                    }}
                  >
                    <Phone size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};