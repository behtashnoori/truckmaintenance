import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { MapPin } from 'lucide-react';

interface CityFilterProps {
  cities: string[];
  value?: string;
  onValueChange: (value: string) => void;
}

export const CityFilter: React.FC<CityFilterProps> = ({ cities, value = 'all', onValueChange }) => {
  return (
    <div className="flex items-center gap-2 min-w-0">
      <MapPin size={16} className="text-muted-foreground flex-shrink-0" />
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="w-full min-w-[120px] h-9 text-sm">
          <SelectValue placeholder="انتخاب شهر" />
        </SelectTrigger>
        <SelectContent className="bg-card border border-border">
          <SelectItem value="all" className="hover:bg-accent">همه شهرها</SelectItem>
          {cities.map((city) => (
            <SelectItem key={city} value={city} className="hover:bg-accent">
              {city}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
