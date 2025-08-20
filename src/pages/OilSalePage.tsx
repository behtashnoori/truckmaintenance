import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';

interface OilProvider {
  id: string;
  name: string;
  phone: string;
  address: string;
  city: string;
  county: string;
}

const oilProviders: Record<string, Record<string, OilProvider[]>> = {
  'تهران': {
    'تهران': [
      { id: '1', name: 'فروش روغن پارس', phone: '0211111111', address: 'تهران، خیابان انقلاب', city: 'تهران', county: 'تهران' },
    ],
    'ری': [
      { id: '2', name: 'نمایندگی روغن ری', phone: '0212222222', address: 'ری، میدان شهرری', city: 'تهران', county: 'ری' },
    ],
  },
  'اصفهان': {
    'اصفهان': [
      { id: '3', name: 'روغن فروشی اصفهان', phone: '0313333333', address: 'اصفهان، میدان نقش جهان', city: 'اصفهان', county: 'اصفهان' },
    ],
    'کاشان': [
      { id: '4', name: 'روغن کاشان', phone: '0314444444', address: 'کاشان، خیابان امیرکبیر', city: 'اصفهان', county: 'کاشان' },
    ],
  },
};

export const OilSalePage: React.FC = () => {
  const [selectedCity, setSelectedCity] = useState<string>('');
  const [selectedCounty, setSelectedCounty] = useState<string>('');

  const cities = Object.keys(oilProviders);
  const counties = selectedCity ? Object.keys(oilProviders[selectedCity]) : [];

  let providers: OilProvider[] = [];
  if (selectedCity) {
    if (selectedCounty) {
      providers = oilProviders[selectedCity][selectedCounty];
    } else {
      providers = Object.values(oilProviders[selectedCity]).flat();
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="فروش روغن" />
      <div className="p-4 space-y-4">
        <div className="grid gap-4">
          <Select onValueChange={(value) => { setSelectedCity(value); setSelectedCounty(''); }}>
            <SelectTrigger>
              <SelectValue placeholder="انتخاب شهر" />
            </SelectTrigger>
            <SelectContent>
              {cities.map((city) => (
                <SelectItem key={city} value={city}>
                  {city}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {selectedCity && (
            <Select onValueChange={setSelectedCounty}>
              <SelectTrigger>
                <SelectValue placeholder="انتخاب شهرستان" />
              </SelectTrigger>
              <SelectContent>
                {counties.map((county) => (
                  <SelectItem key={county} value={county}>
                    {county}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        <div className="space-y-4">
          {providers.map((provider) => (
            <div key={provider.id} className="bg-card p-4 rounded-lg shadow-card border">
              <h3 className="font-semibold mb-2">{provider.name}</h3>
              <p className="text-sm text-muted-foreground mb-1">{provider.address}</p>
              <p className="text-sm">تلفن: {provider.phone}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default OilSalePage;
