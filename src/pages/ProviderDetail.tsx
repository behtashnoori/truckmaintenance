import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { PageNavigation } from '@/components/PageNavigation';
import { VehicleChips } from '@/components/VehicleChips';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api, Provider } from '@/lib/api';
import { Phone, MapPin, LoaderCircle, Clock, Radius } from 'lucide-react';
import { MapViewer } from '@/components/MapViewer';
// import { NavigationModal } from '@/components/NavigationModal'; // مخفی شده


export const ProviderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [provider, setProvider] = useState<Provider | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // const [showNavigationModal, setShowNavigationModal] = useState(false); // مخفی شده

  useEffect(() => {
    if (!id) return;
    fetchProvider();
  }, [id]);

  const fetchProvider = async () => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);

    try {
      // Use fetch directly to get provider details
      const response = await fetch(`/api/public/providers/${id}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Provider Detail API Response:', data); // Debug log
        
        if (data.success && data.data) {
          setProvider(data.data);
        } else {
          setError(data.error || 'خطا در بارگذاری اطلاعات');
        }
      } else {
        setError('خطا در ارتباط با سرور');
      }
    } catch (err) {
      console.error('Error fetching provider:', err);
      setError('خطا در ارتباط با سرور');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCall = () => {
    if (provider?.phone) {
      window.location.href = `tel:${provider.phone}`;
    }
  };

  // const handleNavigationClick = () => {
  //   setShowNavigationModal(true);
  // }; // مخفی شده

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
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="جزئیات ارائه‌دهنده" backTo="previous" />
      
      <div className="flex-1 p-6">
        <div className="max-w-md mx-auto space-y-6">
          
          <div className="text-center space-y-6">
            {/* Header */}
            <div>
              <div className="flex items-center justify-center gap-3 mb-2">
                <h1 className="text-2xl font-bold">{provider.name}</h1>
                {provider.is_24_7 && (
                  <Badge variant="success" className="flex items-center gap-1">
                    <Clock size={16} />
                    ۲۴/۷
                  </Badge>
                )}
              </div>
              <p className="text-muted-foreground">{provider.address}</p>
            </div>

            {/* Coverage Info */}
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 text-muted-foreground text-sm mb-4">
                <Radius size={16} />
                <span>پوشش تا {provider.radius_km || 50} کیلومتر</span>
              </div>
            </div>

            {/* Call Button */}
            <Button 
              onClick={handleCall}
              size="lg"
              className="w-full"
            >
              <Phone className="ml-2" size={20} />
              تماس با {provider.name}
            </Button>

            {/* Services */}
            <div>
              <h3 className="text-lg font-semibold mb-3">خدمات ارائه‌شده</h3>
              <div className="flex flex-wrap gap-2 justify-center">
                {provider.categories && provider.categories.length > 0 ? (
                  provider.categories.map((category) => (
                    <Badge key={category} variant="secondary">
                      {category}
                    </Badge>
                  ))
                ) : (
                  <p className="text-muted-foreground">خدمات تعریف نشده</p>
                )}
              </div>
            </div>

            {/* Vehicle Types */}
            <div>
              <h3 className="text-lg font-semibold mb-3">وسایل نقلیه قابل سرویس</h3>
              <div className="flex justify-center">
                {provider.vehicle_types && provider.vehicle_types.length > 0 ? (
                  <VehicleChips vehicleTypes={provider.vehicle_types} />
                ) : (
                  <p className="text-muted-foreground">همه انواع وسایل نقلیه</p>
                )}
              </div>
            </div>

            {/* Map & Navigation */}
            {provider.location ? (
              <div>
                <h3 className="text-lg font-semibold mb-3">موقعیت و مسیریابی</h3>
                <MapViewer 
                  lat={provider.location.lat} 
                  lon={provider.location.lon}
                  title={provider.name}
                  height={250}
                />
                
                {/* Navigation Button - مخفی شده */}
                {/* <Button 
                  onClick={handleNavigationClick}
                  className="w-full mt-3"
                  size="lg"
                >
                  <Navigation className="mr-2 h-4 w-4" />
                  مسیریابی
                </Button> */}
              </div>
            ) : (
              <div className="bg-muted rounded-lg h-48 flex items-center justify-center">
                <div className="text-center text-muted-foreground">
                  <MapPin size={32} className="mx-auto mb-2" />
                  <p className="text-sm">موقعیت نامشخص</p>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>

      {/* Navigation Modal - مخفی شده */}
      {/* {provider && (
        <NavigationModal
          isOpen={showNavigationModal}
          onClose={() => setShowNavigationModal(false)}
          providerLocation={{
            lat: provider.location.lat,
            lon: provider.location.lon
          }}
          providerName={provider.name}
        />
      )} */}
    </div>
  );
};