import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';

interface Seller {
  id: number;
  name: string;
  phone: string;
  address: string;
  province: string;
  city: string;
}

const sellers: Seller[] = [
  { id: 1, name: 'فروشگاه روغن تهران', phone: '+989121234567', address: 'تهران، خیابان انقلاب', province: 'تهران', city: 'تهران' },
  { id: 2, name: 'نمایندگی فیلتر کرج', phone: '+989126789012', address: 'کرج، خیابان اصلی', province: 'البرز', city: 'کرج' },
  { id: 3, name: 'فروشگاه روغن اصفهان', phone: '+989131234567', address: 'اصفهان، میدان نقش جهان', province: 'اصفهان', city: 'اصفهان' }
];

export const OilFilterPage: React.FC = () => {
  const [province, setProvince] = useState('');
  const [city, setCity] = useState('');

  const provinces = Array.from(new Set(sellers.map(s => s.province)));
  const cities = province ? Array.from(new Set(sellers.filter(s => s.province === province).map(s => s.city))) : [];

  const filtered = sellers.filter(s => {
    if (city) return s.city === city;
    if (province) return s.province === province;
    return true;
  });

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="فروش روغن و فیلتر" />
      <div className="p-4 space-y-4 flex-1">
        <Select value={province} onValueChange={(v) => { setProvince(v); setCity(''); }}>
          <SelectTrigger>
            <SelectValue placeholder="انتخاب استان" />
          </SelectTrigger>
          <SelectContent>
            {provinces.map((p) => (
              <SelectItem key={p} value={p}>{p}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        {cities.length > 0 && (
          <Select value={city} onValueChange={setCity}>
            <SelectTrigger>
              <SelectValue placeholder="انتخاب شهر" />
            </SelectTrigger>
            <SelectContent>
              {cities.map((c) => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        <div className="space-y-4">
          {filtered.map((s) => (
            <div key={s.id} className="p-4 border rounded-lg">
              <h3 className="font-semibold">{s.name}</h3>
              <p className="text-sm text-muted-foreground">{s.address}</p>
              <p className="text-sm">{s.phone}</p>
            </div>
          ))}
          {filtered.length === 0 && (
            <p className="text-center text-muted-foreground">هیچ فروشنده‌ای یافت نشد</p>
          )}
        </div>
      </div>
    </div>
  );
};
