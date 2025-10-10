import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { CategorySelector } from '@/components/CategorySelector';
import { VehicleFilter } from '@/components/VehicleFilter';
import { LocationSelector } from '@/components/LocationSelector';
import { ProviderCard } from '@/components/ProviderCard';
import { Button } from '@/components/ui/button';
import { api, ProviderSearchResult, ServiceCategory, VehicleType } from '@/lib/api';
import { RefreshCw, MapPin, LoaderCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useLocation } from '@/contexts/LocationContext';

interface CategoryInfo {
  id: ServiceCategory;
  title: string;
  subtitle: string;
  subcategories: string[];
}

interface DBCategory {
  id: number;
  name: string;
}

// Fallback categories if database is not available
const fallbackCategoryMap: Record<string, CategoryInfo> = {
  'مکانیکی': {
    id: 'مکانیکی' as ServiceCategory,
    title: 'مکانیکی',
    subtitle: 'خدمات مکانیکی خودروهای سنگین',
    subcategories: ['تعمیر موتور', 'تعمیر گیربکس', 'تعمیر ترمز']
  },
  'تعویض-روغن': {
    id: 'تعویض-روغن' as ServiceCategory,
    title: 'تعویض روغن',
    subtitle: 'تعویض روغن و فیلتر',
    subcategories: ['روغن موتور', 'فیلتر روغن', 'روغن گیربکس']
  },
  'لوازم-یدکی': {
    id: 'لوازم-یدکی' as ServiceCategory,
    title: 'لوازم یدکی',
    subtitle: 'فروش و تامین لوازم یدکی',
    subcategories: ['قطعات موتور', 'قطعات گیربکس', 'قطعات ترمز']
  }
};

interface LocationOption {
  name: string;
  lat: number;
  lon: number;
  type: 'province' | 'city';
}

export const CategoryPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { lat, lon, updateLocation } = useLocation();
  
  const [providers, setProviders] = useState<ProviderSearchResult[]>([]);
  const [filteredProviders, setFilteredProviders] = useState<ProviderSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVehicle, setSelectedVehicle] = useState<VehicleType | 'all'>('all');
  const [manualLocation, setManualLocation] = useState<{lat: number; lon: number} | null>(null);
  const [selectedLocationName, setSelectedLocationName] = useState<string | undefined>();
  const [locations, setLocations] = useState<LocationOption[]>([]);
  const [locationsLoading, setLocationsLoading] = useState(false);
  const [categories, setCategories] = useState<DBCategory[]>([]);
  const [categoryInfo, setCategoryInfo] = useState<CategoryInfo | null>(null);

  // Load categories from API
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await fetch('/api/public/categories');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data) {
            setCategories(data.data);
          }
        }
      } catch (error) {
        console.error('Error loading categories:', error);
      }
    };

    loadCategories();
  }, []);

  // Set category info based on slug and loaded categories
  useEffect(() => {
    if (slug && categories.length > 0) {
      // Try to find category by slug (converted from name)
      const category = categories.find(cat => 
        cat.name.toLowerCase().replace(/\s+/g, '-') === slug
      );
      
      if (category) {
        setCategoryInfo({
          id: category.name.toLowerCase().replace(/\s+/g, '-') as ServiceCategory,
          title: category.name,
          subtitle: `${category.name} - خدمات تخصصی`,
          subcategories: [`${category.name} تخصصی`, 'تعمیرات', 'نصب']
        });
      } else if (fallbackCategoryMap[slug]) {
        setCategoryInfo(fallbackCategoryMap[slug]);
      }
    }
  }, [slug, categories]);

  // Load locations from API
  useEffect(() => {
    const loadLocations = async () => {
      setLocationsLoading(true);
      try {
        const response = await api.getLocations();
        if (response.success && response.data) {
          setLocations(response.data);
        } else {
          toast({
            title: "خطا در بارگذاری استان‌ها",
            description: response.error || "لطفاً دوباره تلاش کنید",
            variant: "destructive",
          });
        }
      } catch (error) {
        toast({
          title: "خطا در بارگذاری استان‌ها",
          description: "لطفاً دوباره تلاش کنید",
          variant: "destructive",
        });
      } finally {
        setLocationsLoading(false);
      }
    };

    if (categoryInfo?.id === 'oil') {
      loadLocations();
    }
  }, [categoryInfo]);

  useEffect(() => {
    if (!categoryInfo) {
      navigate('/services');
      return;
    }

    if (categoryInfo.id === 'oil') {
      if (!manualLocation) {
        setIsLoading(false);
        return;
      }
    } else {
      if (!lat || !lon) {
        navigate('/location-error');
        return;
      }
    }

    fetchProviders();
  }, [lat, lon, categoryInfo, manualLocation]);

  useEffect(() => {
    applyVehicleFilter();
  }, [selectedVehicle, providers]);

  // Set manualLocation when selectedLocationName changes
  useEffect(() => {
    if (selectedLocationName) {
      const location = locations.find(loc => loc.name === selectedLocationName);
      if (location) {
        setManualLocation({ lat: location.lat, lon: location.lon });
      }
    }
  }, [selectedLocationName]);

  const fetchProviders = async () => {
    if (!categoryInfo) return;

    setIsLoading(true);
    setError(null);

    const searchLat = categoryInfo.id === 'oil' ? manualLocation?.lat : lat!;
    const searchLon = categoryInfo.id === 'oil' ? manualLocation?.lon : lon!;
    if (searchLat == null || searchLon == null) {
      setIsLoading(false);
      return;
    }

    const response = await api.searchProviders(searchLat, searchLon, categoryInfo.id);
    
    if (response.success && response.data) {
      // Sort by distance
      const sortedProviders = response.data.sort((a, b) => a.distance_km - b.distance_km);
      setProviders(sortedProviders);
    } else {
      setError(response.error || 'خطا در بارگذاری نتایج');
    }
    
    setIsLoading(false);
  };

  const applyVehicleFilter = () => {
    let filtered = providers;
    
    if (selectedVehicle && selectedVehicle !== 'all') {
      filtered = providers.filter(provider => 
        provider.vehicle_types.includes(selectedVehicle as VehicleType)
      );
    }
    
    setFilteredProviders(filtered);
  };

  const handleCategoryChange = (newCategory: ServiceCategory) => {
    const slugMap: Record<ServiceCategory, string> = {
      roadside: 'roadside',
      tire: 'tyre-wheel',
      recovery: 'recovery-accident',
      oil: 'oil-filter'
    };
    
    navigate(`/c/${slugMap[newCategory]}`);
  };

  const handleRefreshLocation = async () => {
    setIsRefreshing(true);
    try {
      await updateLocation();
      toast({
        title: "موقعیت به‌روزرسانی شد",
        description: "در حال بارگذاری نتایج جدید...",
      });
      fetchProviders();
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

  if (!categoryInfo) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title={categoryInfo.title} />
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
      <Header title={categoryInfo.title} backTo="services" />
      
      {/* Category Info */}
      <div className="gradient-hero text-white p-6 text-center">
        <div className="max-w-md mx-auto">
          <h2 className="text-xl font-bold mb-1 text-shadow-white">{categoryInfo.title}</h2>
          <p className="text-sm opacity-90 text-shadow-white">{categoryInfo.subtitle}</p>
        </div>
      </div>
      
      {/* Filter Bar */}
      <div className="sticky top-16 z-40 bg-background/95 backdrop-blur-sm border-b p-4">
        <div className="space-y-3">
          <CategorySelector
            selectedCategory={categoryInfo.id}
            onCategorySelect={handleCategoryChange}
            variant="compact"
          />
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <VehicleFilter
                value={selectedVehicle}
                onValueChange={setSelectedVehicle}
              />
            </div>
            {categoryInfo.id === 'oil' ? (
              locationsLoading ? (
                <div className="flex items-center gap-2 min-w-0">
                  <MapPin size={16} className="text-muted-foreground flex-shrink-0" />
                  <div className="w-24 h-9 bg-muted animate-pulse rounded"></div>
                </div>
              ) : (
                <LocationSelector
                  locations={locations}
                  value={selectedLocationName}
                  onSelect={(loc) => {
                    setSelectedLocationName(loc.name);
                    setManualLocation({ lat: loc.lat, lon: loc.lon });
                  }}
                />
              )
            ) : (
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
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 p-4">
        {categoryInfo.id === 'oil' && !manualLocation ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">لطفاً استان یا شهر را انتخاب کنید</p>
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={fetchProviders} variant="outline">
              تلاش مجدد
            </Button>
          </div>
        ) : filteredProviders.length === 0 ? (
          <div className="text-center py-8">
            <MapPin size={48} className="mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">هیچ خدماتی یافت نشد</h3>
            <p className="text-muted-foreground mb-4">
              {selectedVehicle && selectedVehicle !== 'all'
                ? `نتیجه‌ای برای این دسته با فیلتر ${selectedVehicle === 'truck' ? 'کامیون' : selectedVehicle === 'semi' ? 'تریلی' : 'اتوبوس'} پیدا نشد.`
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
              {filteredProviders.length} ارائه‌دهنده یافت شد
              {selectedVehicle && selectedVehicle !== 'all' && (
                <span className="mr-1">
                  برای {selectedVehicle === 'truck' ? 'کامیون' : selectedVehicle === 'semi' ? 'تریلی' : 'اتوبوس'}
                </span>
              )}
            </div>

            {filteredProviders.map((provider) => (
              <ProviderCard key={provider.id} provider={provider} />
            ))}
            
          </div>
        )}
      </div>
      
    </div>
  );
};