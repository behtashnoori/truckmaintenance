import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Store {
  id: number;
  name: string;
  phone: string;
  address: string;
  province: string;
  city: string;
}

const stores: Store[] = [
  {
    id: 1,
    name: 'فروشگاه روغن تهران',
    phone: '021-11111111',
    address: 'تهران، خیابان مثال ۱',
    province: 'تهران',
    city: 'تهران',
  },
  {
    id: 2,
    name: 'فیلتر فروشی کرج',
    phone: '026-22222222',
    address: 'البرز، کرج، خیابان مثال ۲',
    province: 'البرز',
    city: 'کرج',
  },
  {
    id: 3,
    name: 'روغن موتور اصفهان',
    phone: '031-33333333',
    address: 'اصفهان، خیابان مثال ۳',
    province: 'اصفهان',
    city: 'اصفهان',
  },
  {
    id: 4,
    name: 'فیلتر فروشی نجف‌آباد',
    phone: '031-44444444',
    address: 'اصفهان، نجف‌آباد، خیابان مثال ۴',
    province: 'اصفهان',
    city: 'نجف‌آباد',
  },
];

export const OilFilterPage: React.FC = () => {
  const [province, setProvince] = useState<string>();
  const [city, setCity] = useState<string>();

  const provinces = Array.from(new Set(stores.map((s) => s.province)));
  const cities = province
    ? Array.from(new Set(stores.filter((s) => s.province === province).map((s) => s.city)))
    : [];

  const results = stores.filter((s) => {
    if (!province) return false;
    if (!city) return s.province === province;
    return s.province === province && s.city === city;
  });

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="فروش روغن و فیلتر" />
      <div className="flex-1 p-6 space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="text-sm font-medium mb-2 block">استان</label>
            <Select
              value={province}
              onValueChange={(v) => {
                setProvince(v);
                setCity(undefined);
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="انتخاب استان" />
              </SelectTrigger>
              <SelectContent>
                {provinces.map((p) => (
                  <SelectItem key={p} value={p}>
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {province && (
            <div>
              <label className="text-sm font-medium mb-2 block">شهر</label>
              <Select value={city} onValueChange={setCity}>
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
          )}
        </div>
        <div className="space-y-4">
          {results.map((store) => (
            <div
              key={store.id}
              className="border rounded-lg p-4 shadow-card"
            >
              <h3 className="font-semibold text-mobile-base">{store.name}</h3>
              <p className="text-sm text-muted-foreground">
                {store.address}
              </p>
              <p className="text-sm mt-1">تلفن: {store.phone}</p>
            </div>
          ))}
          {province && results.length === 0 && (
            <p className="text-sm text-muted-foreground">هیچ موردی یافت نشد</p>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default OilFilterPage;
