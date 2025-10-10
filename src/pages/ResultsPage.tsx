import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { CategorySelector } from '@/components/CategorySelector';
import { VehicleFilter } from '@/components/VehicleFilter';
import { ProviderCard } from '@/components/ProviderCard';
import { Button } from '@/components/ui/button';
import { api, ProviderSearchResult, ServiceCategory, VehicleType } from '@/lib/api';
import { RefreshCw, MapPin, LoaderCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useLocation } from '@/contexts/LocationContext';

export const ResultsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { updateLocation } = useLocation();
  const [providers, setProviders] = useState<ProviderSearchResult[]>([]);
  const [allProviders, setAllProviders] = useState<ProviderSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const lat = parseFloat(searchParams.get('lat') || '0');
  const lon = parseFloat(searchParams.get('lon') || '0');
  const category = searchParams.get('category') as ServiceCategory | null;
  const vehicle = searchParams.get('vehicle') as VehicleType | 'all' | null;

  useEffect(() => {
    if (!lat || !lon) {
      navigate('/location-error');
      return;
    }

    fetchProviders();
  }, [lat, lon, category]);

  useEffect(() => {
    applyFilters();
  }, [vehicle, allProviders]);

  const fetchProviders = async () => {
    setIsLoading(true);
    setError(null);

    const response = await api.searchProviders(lat, lon, category || undefined);
    
    if (response.success && response.data) {
      setAllProviders(response.data);
    } else {
      setError(response.error || 'خطا در بارگذاری نتایج');
    }
    
    setIsLoading(false);
  };

  const applyFilters = () => {
    let filtered = allProviders;
    
    if (vehicle && vehicle !== 'all') {
      filtered = allProviders.filter(provider => 
        provider.vehicle_types.includes(vehicle as VehicleType)
      );
    }
    
    setProviders(filtered);
  };

  const handleCategoryChange = (newCategory: ServiceCategory) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('category', newCategory);
    setSearchParams(newParams);
  };

  const handleVehicleChange = (newVehicle: VehicleType | 'all') => {
    const newParams = new URLSearchParams(searchParams);
    if (newVehicle === 'all') {
      newParams.delete('vehicle');
    } else {
      newParams.set('vehicle', newVehicle);
    }
    setSearchParams(newParams);
  };

  const handleRefreshLocation = async () => {
    setIsRefreshing(true);
    try {
      await updateLocation();
      toast({
        title: "موقعیت به‌روزرسانی شد",
        description: "در حال بارگذاری نتایج جدید...",
      });
      // Reload page with new location
      window.location.reload();
    } catch (error) {
      toast({
        title: "خطا در به‌روزرسانی موقعیت",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsRefreshing(false);
    }
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
      <Header title="نتایج جستجو" backTo="services" />
      
      {/* Filter Bar */}
      <div className="sticky top-16 z-40 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="space-y-3">
          <CategorySelector
            selectedCategory={category || undefined}
            onCategorySelect={handleCategoryChange}
            variant="compact"
          />
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <VehicleFilter
                value={(vehicle as VehicleType) || 'all'}
                onValueChange={handleVehicleChange}
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefreshLocation}
              disabled={isRefreshing}
              className="flex items-center gap-2 flex-shrink-0"
            >
              <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
              {isRefreshing ? 'در حال به‌روزرسانی...' : 'به‌روزرسانی موقعیت'}
            </Button>
          </div>
        </div>
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
              {vehicle && vehicle !== 'all' 
                ? `نتیجه‌ای برای این دسته با فیلتر ${vehicle === 'truck' ? 'کامیون' : vehicle === 'semi' ? 'تریلی' : 'اتوبوس'} پیدا نشد.`
                : 'در این منطقه ارائه‌دهنده‌ای برای این نوع خدمات یافت نشد'
              }
            </p>
            <Button
              onClick={() => navigate('/services')}
              variant="outline"
            >
              جستجوی جدید
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground mb-4">
              {providers.length} ارائه‌دهنده یافت شد
              {vehicle && vehicle !== 'all' && (
                <span className="mr-1">
                  برای {vehicle === 'truck' ? 'کامیون' : vehicle === 'semi' ? 'تریلی' : 'اتوبوس'}
                </span>
              )}
            </div>
            
            {providers.map((provider) => (
              <ProviderCard key={provider.id} provider={provider} />
            ))}
            
          </div>
        )}
      </div>
    </div>
  );
};