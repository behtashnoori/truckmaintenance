import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface Seller {
  id: number;
  name: string;
  province: string;
  city: string;
  address: string;
  phone: string;
}

const sellers: Seller[] = [
  {
    id: 1,
    name: 'فروشگاه روغن برتر',
    province: 'تهران',
    city: 'تهران',
    address: 'خیابان آزادی',
    phone: '+989123456789',
  },
  {
    id: 2,
    name: 'مرکز روغن اصفهان',
    province: 'اصفهان',
    city: 'اصفهان',
    address: 'خیابان چهارباغ بالا',
    phone: '+989112223334',
  },
  {
    id: 3,
    name: 'فروشگاه فیلتر تبریز',
    province: 'آذربایجان شرقی',
    city: 'تبریز',
    address: 'خیابان ولیعصر',
    phone: '+989114445556',
  },
];

export const OilFilterPage: React.FC = () => {
  const [selectedCity, setSelectedCity] = useState<string>();

  const cities = Array.from(new Set(sellers.map((s) => s.city)));
  const citySellers = sellers.filter((s) => s.city === selectedCity);

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="فروش روغن و فیلتر" />
      <Tabs defaultValue="province" className="flex-1 p-4">
        <TabsList className="grid grid-cols-2 mb-4">
          <TabsTrigger value="province">استان</TabsTrigger>
          <TabsTrigger value="city">شهر</TabsTrigger>
        </TabsList>
        <TabsContent value="province" className="space-y-4">
          {sellers.map((seller) => (
            <div
              key={seller.id}
              className="bg-card p-4 rounded-lg shadow-card border"
            >
              <h3 className="font-semibold text-mobile-base mb-1">{seller.name}</h3>
              <p className="text-sm text-muted-foreground mb-1">
                {seller.province} - {seller.city}
              </p>
              <p className="text-sm text-muted-foreground mb-2">{seller.address}</p>
              <Button asChild variant="secondary" size="sm">
                <a href={`tel:${seller.phone}`}>تماس</a>
              </Button>
            </div>
          ))}
        </TabsContent>
        <TabsContent value="city" className="space-y-4">
          <Select onValueChange={setSelectedCity}>
            <SelectTrigger className="w-full">
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
          {selectedCity ? (
            citySellers.length > 0 ? (
              citySellers.map((seller) => (
                <div
                  key={seller.id}
                  className="bg-card p-4 rounded-lg shadow-card border"
                >
                  <h3 className="font-semibold text-mobile-base mb-1">{seller.name}</h3>
                  <p className="text-sm text-muted-foreground mb-1">
                    {seller.province} - {seller.city}
                  </p>
                  <p className="text-sm text-muted-foreground mb-2">{seller.address}</p>
                  <Button asChild variant="secondary" size="sm">
                    <a href={`tel:${seller.phone}`}>تماس</a>
                  </Button>
                </div>
              ))
            ) : (
              <p className="text-center text-muted-foreground">
                فروشنده‌ای یافت نشد
              </p>
            )
          ) : (
            <p className="text-center text-muted-foreground">
              لطفاً شهر را انتخاب کنید
            </p>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OilFilterPage;
