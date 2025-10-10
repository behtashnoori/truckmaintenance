import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { ServiceCategory } from '@/lib/api';
import { Truck, Settings, AlertTriangle, Droplet, Tag } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

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

interface Category {
  id: number;
  name: string;
  companies_count?: number;
}

// Default categories as fallback
const defaultCategories = [
  {
    id: 'roadside' as ServiceCategory,
    title: 'خدمات جاده‌ای',
    description: 'پارکینگ، سوخت، رستوران',
    icon: Truck,
    disabled: true,
  },
  {
    id: 'tire' as ServiceCategory,
    title: 'لاستیک و رینگ',
    description: 'تعویض و تعمیر لاستیک',
    icon: Settings,
    disabled: true,
  },
  {
    id: 'recovery' as ServiceCategory,
    title: 'امداد و حادثه',
    description: 'یدک‌کش و تعمیرات اضطراری',
    icon: AlertTriangle,
    disabled: true,
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
  const [categories, setCategories] = useState(defaultCategories);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/public/categories');
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          const apiCategories = data.data.map((cat: Category) => ({
            id: cat.name.toLowerCase().replace(/\s+/g, '-') as ServiceCategory,
            title: cat.name,
            description: `${cat.companies_count || 0} ارائه‌دهنده`,
            icon: Tag,
            disabled: false,
          }));
          setCategories(apiCategories);
        }
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Keep default categories on error
    } finally {
      setIsLoading(false);
    }
  };

  const isSelected = (categoryId: ServiceCategory) => 
    multiSelect ? selectedCategories.includes(categoryId) : selectedCategory === categoryId;

  const handleCategoryClick = (categoryId: ServiceCategory) => {
    if (directNavigation && onDirectNavigate) {
      onDirectNavigate(categoryId);
    } else {
      onCategorySelect(categoryId);
    }
  };

  const handleCategoryNavigation = (categoryId: ServiceCategory, providerCount: number) => {
    if (providerCount === 0) {
      // Show friendly toast message for categories with 0 providers
      toast({
        title: "هنوز ارائه‌دهنده‌ای ثبت‌نام نکرده",
        description: `در حوزه ${categoryId} هنوز کسی ثبت‌نام نکرده است. شما می‌توانید اولین ارائه‌دهنده باشید!`,
        variant: "default",
      });
      return;
    }
    
    // Navigate to category providers page
    window.location.href = `/category/${categoryId}`;
  };
  if (variant === 'compact') {
    return (
      <div className={`flex gap-2 ${className}`}>
        {categories.map((category) => {
          const Icon = category.icon;
          const categorySelected = isSelected(category.id);
          const providerCount = parseInt(category.description.split(' ')[0]) || 0;
          
        return (
          <Button
            key={category.id}
            variant={categorySelected ? 'default' : 'outline'}
            size="sm"
            onClick={category.disabled ? undefined : () => handleCategoryNavigation(category.id, providerCount)}
            className="flex-1"
            disabled={category.disabled}
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
        const providerCount = parseInt(category.description.split(' ')[0]) || 0;

        return (
          <Button
            key={category.id}
            variant={categorySelected ? 'default' : 'outline'}
            className="h-auto p-4 flex flex-col items-center text-center"
            onClick={category.disabled ? undefined : () => handleCategoryNavigation(category.id, providerCount)}
            disabled={category.disabled}
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