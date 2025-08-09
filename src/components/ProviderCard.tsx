import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProviderSearchResult } from '@/lib/api';
import { VehicleChips } from '@/components/VehicleChips';
import { Phone, MapPin, Clock } from 'lucide-react';

interface ProviderCardProps {
  provider: ProviderSearchResult;
}

export const ProviderCard: React.FC<ProviderCardProps> = ({ provider }) => {
  const navigate = useNavigate();

  const handleCall = (e: React.MouseEvent) => {
    e.stopPropagation();
    window.location.href = `tel:${provider.phone}`;
  };

  const handleCardClick = () => {
    navigate(`/provider/${provider.id}`);
  };

  return (
    <div
      className="bg-card p-4 rounded-lg shadow-card border hover:shadow-floating transition-smooth cursor-pointer"
      onClick={handleCardClick}
    >
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-mobile-base truncate">
              {provider.name}
            </h3>
            {provider.is_24_7 && (
              <Badge variant="success" className="flex items-center gap-1 flex-shrink-0">
                <Clock size={12} />
                ۲۴/۷
              </Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground mb-2 line-clamp-1">
            {provider.address}
          </p>
          <div className="flex items-center gap-1 text-sm text-primary mb-2">
            <MapPin size={16} />
            {provider.distance_km.toFixed(1)} کیلومتر
          </div>
          <p className="text-xs text-muted-foreground mb-2">
            پوشش تا {provider.radius_km} کیلومتر
          </p>
          <VehicleChips vehicleTypes={provider.vehicle_types} size="sm" />
        </div>
        
        <Button
          variant="secondary"
          size="icon-sm"
          onClick={handleCall}
          className="flex-shrink-0"
        >
          <Phone size={16} />
        </Button>
      </div>
    </div>
  );
};