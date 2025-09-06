import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { CategorySelector } from '@/components/CategorySelector';
import { Footer } from '@/components/Footer';
import { useLocation } from '@/contexts/LocationContext';
import { ServiceCategory } from '@/lib/api';
import { Truck } from 'lucide-react';

export const SearchPage: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<ServiceCategory | undefined>();
  const { lat, lon } = useLocation();
  const navigate = useNavigate();

  const handleDirectNavigation = (category: ServiceCategory) => {
    if (category !== 'oil' && (!lat || !lon)) {
      navigate('/location-error');
      return;
    }

    const slugMap: Record<ServiceCategory, string> = {
      roadside: 'roadside',
      tire: 'tyre-wheel',
      recovery: 'recovery-accident',
      oil: 'oil-filter'
    };
    navigate(`/c/${slugMap[category]}`);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <div className="gradient-hero text-white p-6 text-center">
        <div className="max-w-md mx-auto">
          <Truck size={48} className="mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-shadow-white">
            بازارگاه خدمات اضطراری و تعمیرات خودروهای سنگین
          </h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 space-y-6">
        {/* Category Selection */}
        <div>
          <h2 className="text-mobile-lg font-semibold mb-4">نوع خدمات مورد نیاز</h2>
          <CategorySelector
            selectedCategory={selectedCategory}
            onCategorySelect={setSelectedCategory}
            directNavigation={true}
            onDirectNavigate={handleDirectNavigation}
          />
        </div>

        {/* Provider Registration Link */}
        <div className="text-center pt-4">
          <p className="text-sm text-muted-foreground mb-2">
            ارائه‌دهنده خدمات هستید؟
          </p>
          <Button
            variant="outline"
            onClick={() => navigate('/signup')}
            className="w-full"
          >
            ثبت‌نام ارائه‌دهنده
          </Button>
        </div>
      </div>

      <Footer />
    </div>
  );
};