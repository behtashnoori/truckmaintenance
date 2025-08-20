import React from 'react';
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from '@/components/ui/select';
import { cities } from '@/data/locations';

interface LocationSelectorProps {
  city?: string;
  county?: string;
  onCityChange: (value: string) => void;
  onCountyChange: (value: string) => void;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({
  city,
  county,
  onCityChange,
  onCountyChange,
}) => {
  const selectedCity = cities.find(c => c.name === city);

  return (
    <div className="space-y-3">
      <Select
        value={city || ''}
        onValueChange={(value) => {
          onCityChange(value);
          onCountyChange('');
        }}
      >
        <SelectTrigger>
          <SelectValue placeholder="انتخاب شهر" />
        </SelectTrigger>
        <SelectContent>
          {cities.map(c => (
            <SelectItem key={c.name} value={c.name}>
              {c.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {city && (
        <Select value={county || ''} onValueChange={onCountyChange}>
          <SelectTrigger>
            <SelectValue placeholder="انتخاب شهرستان" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">همه شهرستان‌ها</SelectItem>
            {selectedCity?.counties.map(cnt => (
              <SelectItem key={cnt} value={cnt}>
                {cnt}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
    </div>
  );
};
