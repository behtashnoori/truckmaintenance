import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Header } from '@/components/Header';
import { api, RoadsideFacility } from '@/lib/api';
import { MapPin } from 'lucide-react';

export const RoadsidePage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const lat = parseFloat(searchParams.get('lat') || '0');
  const lon = parseFloat(searchParams.get('lon') || '0');
  const [facilities, setFacilities] = useState<RoadsideFacility[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFacilities = async () => {
      setIsLoading(true);
      const response = await api.searchRoadsideFacilities(lat, lon);
      if (response.success && response.data) {
        setFacilities(response.data);
      } else {
        setError(response.error || 'خطا در بارگذاری نتایج');
      }
      setIsLoading(false);
    };
    fetchFacilities();
  }, [lat, lon]);

  const openDirections = (facility: RoadsideFacility) => {
    const url = `https://www.google.com/maps/dir/?api=1&origin=${lat},${lon}&destination=${facility.location.lat},${facility.location.lon}`;
    window.open(url, '_blank');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title="فروش روغن و فیلتر" />
        <div className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground">در حال بارگذاری...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title="فروش روغن و فیلتر" />
        <div className="flex-1 flex items-center justify-center p-4">
          <p className="text-destructive">{error}</p>
        </div>
      </div>
    );
  }

  const groups = {
    restaurant: facilities.filter(f => f.type === 'restaurant'),
    fuel: facilities.filter(f => f.type === 'fuel'),
    parking: facilities.filter(f => f.type === 'parking'),
  };

  const renderList = (items: RoadsideFacility[]) => (
    <div className="space-y-2">
      {items.map(item => (
        <div
          key={item.id}
          className="bg-card p-4 rounded-lg shadow-card cursor-pointer hover:shadow-floating"
          onClick={() => openDirections(item)}
        >
          <h3 className="font-semibold mb-1">{item.name}</h3>
          <p className="text-sm text-muted-foreground mb-1">{item.address}</p>
          <div className="flex items-center gap-1 text-sm text-primary">
            <MapPin size={16} />
            {item.distance_km.toFixed(1)} کیلومتر
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="فروش روغن و فیلتر" />
      <div className="flex-1 p-4 space-y-6">
        {groups.restaurant.length > 0 && (
          <div>
            <h2 className="font-semibold mb-2">رستوران‌ها</h2>
            {renderList(groups.restaurant)}
          </div>
        )}
        {groups.fuel.length > 0 && (
          <div>
            <h2 className="font-semibold mb-2">جایگاه سوخت</h2>
            {renderList(groups.fuel)}
          </div>
        )}
        {groups.parking.length > 0 && (
          <div>
            <h2 className="font-semibold mb-2">پارکینگ</h2>
            {renderList(groups.parking)}
          </div>
        )}
      </div>
    </div>
  );
};
