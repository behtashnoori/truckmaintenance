import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { VehicleType } from '@/lib/api';
import { Truck } from 'lucide-react';

interface VehicleFilterProps {
  value?: VehicleType | 'all';
  onValueChange: (value: VehicleType | 'all') => void;
}

const vehicleTypeLabels: Record<VehicleType | 'all', string> = {
  all: 'همهٔ وسایل',
  truck: 'کامیون',
  semi: 'تریلی',
  bus: 'اتوبوس'
};

export const VehicleFilter: React.FC<VehicleFilterProps> = ({ value = 'all', onValueChange }) => {
  return (
    <div className="flex items-center gap-2 min-w-0">
      <Truck size={16} className="text-muted-foreground flex-shrink-0" />
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="w-full min-w-[120px] h-9 text-sm">
          <SelectValue placeholder="نوع وسیله" />
        </SelectTrigger>
        <SelectContent className="bg-card border border-border">
          {Object.entries(vehicleTypeLabels).map(([key, label]) => (
            <SelectItem key={key} value={key} className="hover:bg-accent">
              {label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};