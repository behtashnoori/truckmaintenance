import React from 'react';
import { Badge } from '@/components/ui/badge';
import { VehicleType } from '@/lib/api';
import { Truck, Bus } from 'lucide-react';

interface VehicleChipsProps {
  vehicleTypes: VehicleType[];
  size?: 'sm' | 'default';
}

const vehicleTypeLabels: Record<VehicleType, string> = {
  truck: 'کامیون',
  semi: 'تریلی',
  bus: 'اتوبوس'
};

const vehicleTypeIcons: Record<VehicleType, React.ElementType> = {
  truck: Truck,
  semi: Truck,
  bus: Bus
};

export const VehicleChips: React.FC<VehicleChipsProps> = ({ vehicleTypes, size = 'default' }) => {
  return (
    <div className="flex flex-wrap gap-1">
      {vehicleTypes.map((type) => {
        const Icon = vehicleTypeIcons[type];
        return (
          <Badge
            key={type}
            variant="secondary"
            className={`flex items-center gap-1 ${
              size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm'
            }`}
          >
            <Icon size={size === 'sm' ? 12 : 14} />
            {vehicleTypeLabels[type]}
          </Badge>
        );
      })}
    </div>
  );
};