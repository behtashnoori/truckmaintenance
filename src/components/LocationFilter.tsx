import React, { useMemo } from 'react';
import { MapPin } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ProviderSearchResult } from '@/lib/api';

interface LocationFilterProps {
  providers: ProviderSearchResult[];
  selectedProvince: string;
  selectedCity: string;
  onProvinceChange: (province: string) => void;
  onCityChange: (city: string) => void;
}

export const LocationFilter: React.FC<LocationFilterProps> = ({
  providers,
  selectedProvince,
  selectedCity,
  onProvinceChange,
  onCityChange,
}) => {
  const provinces = useMemo(
    () => Array.from(new Set(providers.map(p => p.province))),
    [providers]
  );

  const cities = useMemo(() => {
    const filtered =
      selectedProvince === 'all'
        ? providers
        : providers.filter(p => p.province === selectedProvince);
    return Array.from(new Set(filtered.map(p => p.city)));
  }, [providers, selectedProvince]);

  return (
    <div className="flex flex-col sm:flex-row gap-2">
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <MapPin size={16} className="text-muted-foreground flex-shrink-0" />
        <Select
          value={selectedProvince}
          onValueChange={value => {
            onProvinceChange(value);
            onCityChange('all');
          }}
        >
          <SelectTrigger className="w-full min-w-[120px] h-9 text-sm">
            <SelectValue placeholder="استان" />
          </SelectTrigger>
          <SelectContent className="bg-card border border-border">
            <SelectItem value="all">تمام استان‌ها</SelectItem>
            {provinces.map(prov => (
              <SelectItem key={prov} value={prov}>
                {prov}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex items-center gap-2 flex-1 min-w-0">
        <Select value={selectedCity} onValueChange={onCityChange}>
          <SelectTrigger className="w-full min-w-[120px] h-9 text-sm">
            <SelectValue placeholder="شهر" />
          </SelectTrigger>
          <SelectContent className="bg-card border border-border">
            <SelectItem value="all">تمام شهرها</SelectItem>
            {cities.map(city => (
              <SelectItem key={city} value={city}>
                {city}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
