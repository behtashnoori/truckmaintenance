import React, { useState } from 'react';
import { Header } from '@/components/Header';
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from '@/components/ui/select';
import oilFilterData, { OilFilterInfo } from '@/data/oilFilterData';

const OilFilterPage: React.FC = () => {
  const [city, setCity] = useState('');
  const [county, setCounty] = useState('');

  const cities = Object.keys(oilFilterData);
  const counties = city ? Object.keys(oilFilterData[city]) : [];

  const items: OilFilterInfo[] = city
    ? county
      ? oilFilterData[city][county]
      : Object.values(oilFilterData[city]).flat()
    : [];

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="فروش روغن و فیلتر" />
      <div className="p-4 space-y-4">
        <div>
          <Select
            value={city}
            onValueChange={(value) => {
              setCity(value);
              setCounty('');
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="انتخاب شهر" />
            </SelectTrigger>
            <SelectContent>
              {cities.map((c) => (
                <SelectItem key={c} value={c}>
                  {c}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {city && (
          <div>
            <Select value={county} onValueChange={setCounty}>
              <SelectTrigger>
                <SelectValue placeholder="انتخاب شهرستان" />
              </SelectTrigger>
              <SelectContent>
                {counties.map((ct) => (
                  <SelectItem key={ct} value={ct}>
                    {ct}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="border rounded-lg p-4">
              <div className="font-semibold">{item.name}</div>
              <div className="text-sm text-muted-foreground">{item.address}</div>
              <div className="text-sm text-muted-foreground">{item.phone}</div>
            </div>
          ))}
          {city && items.length === 0 && (
            <p className="text-center text-muted-foreground">اطلاعاتی یافت نشد</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default OilFilterPage;
