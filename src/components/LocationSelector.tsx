import React from 'react';
import { MapPin } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface LocationOption {
  name: string;
  lat: number;
  lon: number;
}

interface LocationSelectorProps {
  locations: LocationOption[];
  value?: string;
  onSelect: (location: LocationOption) => void;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({ locations, value, onSelect }) => {
  const handleChange = (val: string) => {
    const loc = locations.find(l => l.name === val);
    if (loc) onSelect(loc);
  };

  return (
    <div className="flex items-center gap-2 min-w-0">
      <MapPin size={16} className="text-muted-foreground flex-shrink-0" />
      <Select value={value} onValueChange={handleChange}>
        <SelectTrigger className="w-full min-w-[120px] h-9 text-sm">
          <SelectValue placeholder="استان یا شهر" />
        </SelectTrigger>
        <SelectContent className="bg-card border border-border max-h-[200px] overflow-y-auto">
          {locations.map(loc => (
            <SelectItem key={loc.name} value={loc.name} className="hover:bg-accent">
              {loc.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
