import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { CategorySelector } from '@/components/CategorySelector';
import { VehicleFilter } from '@/components/VehicleFilter';
import { ProviderCard } from '@/components/ProviderCard';
import { Button } from '@/components/ui/button';
import { api, ProviderSearchResult, ServiceCategory, VehicleType } from '@/lib/api';
import { MapPin, LoaderCircle } from 'lucide-react';

export const ResultsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [providers, setProviders] = useState<ProviderSearchResult[]>([]);
  const [allProviders, setAllProviders] = useState<ProviderSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const category = searchParams.get('category') as ServiceCategory | null;
  const vehicle = searchParams.get('vehicle') as VehicleType | 'all' | null;

  useEffect(() => {
    fetchProviders();
  }, [category]);

  useEffect(() => {
    applyFilters();
  }, [vehicle, allProviders]);

  const fetchProviders = async () => {
    setIsLoading(true);
    setError(null);

    const response = await api.searchProviders(category || undefined);
    
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