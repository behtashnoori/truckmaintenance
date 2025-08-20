import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { VehicleChips } from '@/components/VehicleChips';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { api, Provider } from '@/lib/api';
import { Phone, MapPin, LoaderCircle, ArrowLeft, Clock, Radius } from 'lucide-react';


export const ProviderDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
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
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="جزئیات ارائه‌دهنده" />
      
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

            {/* Distance and Coverage */}
            <div className="space-y-2">
              <div className="flex items-center justify-center gap-2 text-primary">
                <MapPin size={20} />
                <span className="font-semibold">{provider.distance_km.toFixed(1)} کیلومتر فاصله</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-muted-foreground text-sm">
                <Radius size={16} />
                <span>پوشش تا {provider.radius_km} کیلومتر</span>
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
                {provider.categories.map((category) => (
                  <Badge key={category} variant="secondary">
                    {category === 'roadside' ? 'فروش روغن و فیلتر' :
                     category === 'tire' ? 'لاستیک و چرخ' :
                     category === 'recovery' ? 'بازیابی و امداد' : category}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Vehicle Types */}
            <div>
              <h3 className="text-lg font-semibold mb-3">وسایل نقلیه قابل سرویس</h3>
              <div className="flex justify-center">
                <VehicleChips vehicleTypes={provider.vehicle_types} />
              </div>
            </div>

            {/* Map placeholder */}
            <div className="bg-muted rounded-lg h-48 flex items-center justify-center">
              <div className="text-center text-muted-foreground">
                <MapPin size={32} className="mx-auto mb-2" />
                <p className="text-sm">نقشه موقعیت</p>
                <p className="text-xs">عرض: {provider.location.lat.toFixed(6)}</p>
                <p className="text-xs">طول: {provider.location.lon.toFixed(6)}</p>
              </div>
            </div>

            {/* Back Button */}
            <Button 
              onClick={() => navigate(-1)}
              variant="outline"
              className="w-full"
            >
              <ArrowLeft className="ml-2" size={16} />
              بازگشت به نتایج
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};