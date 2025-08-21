import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const provinces: Record<string, string[]> = {
  'تهران': ['تهران', 'شهریار', 'شهر قدس'],
  'اصفهان': ['اصفهان', 'کاشان', 'نجف‌آباد'],
  'آذربایجان شرقی': ['تبریز', 'مراغه', 'مرند'],
};

export const OilFilterPage: React.FC = () => {
  const [province, setProvince] = useState('');
  const [city, setCity] = useState('');

  return (
    <div className="min-h-screen flex flex-col">
      <Header title="فروش روغن و فیلتر" />
      <div className="flex-1 p-6 space-y-6">
        <div>
          <Label className="mb-2 block">استان</Label>
          <Select
            value={province}
            onValueChange={(value) => {
              setProvince(value);
              setCity('');
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="انتخاب استان" />
            </SelectTrigger>
            <SelectContent>
              {Object.keys(provinces).map((p) => (
                <SelectItem key={p} value={p}>
                  {p}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div>
          <Label className="mb-2 block">شهر</Label>
          <Select
            value={city}
            onValueChange={setCity}
            disabled={!province}
          >
            <SelectTrigger>
              <SelectValue placeholder="انتخاب شهر" />
            </SelectTrigger>
            <SelectContent>
              {province &&
                provinces[province].map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};

export default OilFilterPage;
