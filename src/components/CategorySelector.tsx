import React from 'react';
import { Button } from '@/components/ui/button';
import { ServiceCategory } from '@/lib/api';
import { Truck, Settings, AlertTriangle, Droplet } from 'lucide-react';

interface CategorySelectorProps {
  selectedCategory?: ServiceCategory;
  onCategorySelect: (category: ServiceCategory) => void;
  variant?: 'default' | 'compact';
  className?: string;
  multiSelect?: boolean;
  selectedCategories?: ServiceCategory[];
  directNavigation?: boolean;
  onDirectNavigate?: (category: ServiceCategory) => void;
}

const categories = [
  {
    id: 'roadside' as ServiceCategory,
    title: 'خدمات جاده‌ای',
    description: 'پارکینگ، سوخت، رستوران',
    icon: Truck,
  },
  {
    id: 'tire' as ServiceCategory,
    title: 'لاستیک و رینگ',
    description: 'تعویض و تعمیر لاستیک',
    icon: Settings,
  },
  {
    id: 'recovery' as ServiceCategory,
    title: 'امداد و حادثه',
    description: 'یدک‌کش و تعمیرات اضطراری',
    icon: AlertTriangle,
  },
  {
    id: 'oil' as ServiceCategory,
    title: 'فروش روغن و فیلتر',
    description: 'نمایندگی‌ها و فروشگاه‌های روغن',
    icon: Droplet,
  },
];

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  selectedCategory,
  onCategorySelect,
  variant = 'default',
  className = '',
  multiSelect = false,
  selectedCategories = [],
  directNavigation = false,
  onDirectNavigate,
}) => {
  const isSelected = (categoryId: ServiceCategory) => 
    multiSelect ? selectedCategories.includes(categoryId) : selectedCategory === categoryId;

  const handleCategoryClick = (categoryId: ServiceCategory) => {
    if (directNavigation && onDirectNavigate) {
      onDirectNavigate(categoryId);
    } else {
      onCategorySelect(categoryId);
    }
  };
  if (variant === 'compact') {
    return (
      <div className={`flex gap-2 ${className}`}>
        {categories.map((category) => {
          const Icon = category.icon;
          const categorySelected = isSelected(category.id);
          
          return (
            <Button
              key={category.id}
              variant={categorySelected ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleCategoryClick(category.id)}
              className="flex-1"
            >
              <Icon className="ml-1" size={16} />
              {category.title}
            </Button>
          );
        })}
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-2 gap-3 ${className}`}>
      {categories.map((category) => {
        const Icon = category.icon;
        const categorySelected = isSelected(category.id);
        
        return (
          <Button
            key={category.id}
            variant={categorySelected ? 'default' : 'outline'}
            className="h-auto p-4 flex flex-col items-center text-center"
            onClick={() => handleCategoryClick(category.id)}
          >
            <Icon size={32} className="mb-2" />
            <div>
              <div className="font-semibold text-mobile-base">{category.title}</div>
              <div className="text-sm opacity-75 mt-1">{category.description}</div>
            </div>
          </Button>
        );
      })}
    </div>
  );
};