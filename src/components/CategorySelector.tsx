import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { ServiceCategory } from '@/lib/api';
import { Tag } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getCategories, UICategory } from '@/services/categories';

interface CategorySelectorProps {
  selectedCategory?: ServiceCategory;
  onCategorySelect?: (category: ServiceCategory) => void;
  variant?: 'default' | 'compact';
  className?: string;
  multiSelect?: boolean;
  selectedCategories?: string[];
  onMultiSelect?: (categories: string[]) => void;
  directNavigation?: boolean;
  onDirectNavigate?: (category: ServiceCategory) => void;
}

interface CategoryItem {
  id: ServiceCategory;
  title: string;
  description: string;
  icon: any;
  disabled?: boolean;
  originalName?: string;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  selectedCategory,
  onCategorySelect,
  variant = 'default',
  className = '',
  multiSelect = false,
  selectedCategories = [],
  onMultiSelect,
  directNavigation = false,
  onDirectNavigate,
}) => {
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const items = await getCategories();
      const categoryItems: CategoryItem[] = items.map(cat => ({
        id: cat.id as ServiceCategory,
        title: cat.title,
        description: cat.description,
        icon: Tag,
        disabled: false,
        originalName: cat.originalName,
      }));
      setCategories(categoryItems);
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Keep empty array on error - no fallback
    } finally {
      setIsLoading(false);
    }
  };

  const isSelected = (categoryName: string) => 
    multiSelect ? selectedCategories.includes(categoryName) : selectedCategory === categoryName;

  const handleCategoryClick = (categoryName: string, categoryId: ServiceCategory) => {
    if (multiSelect && onMultiSelect) {
      // Toggle category in multi-select mode
      const newSelection = selectedCategories.includes(categoryName)
        ? selectedCategories.filter(c => c !== categoryName)
        : [...selectedCategories, categoryName];
      onMultiSelect(newSelection);
    } else if (directNavigation && onDirectNavigate) {
      onDirectNavigate(categoryId);
    } else if (onCategorySelect) {
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

  // Loading skeleton
  if (isLoading) {
    return (
      <div className={`grid grid-cols-2 gap-3 ${className}`}>
        {Array.from({ length: 4 }).map((_, i) => (
          <Button key={i} variant="outline" className="h-auto p-4 opacity-60" disabled>
            <div className="w-full animate-pulse">
              <div className="h-5 bg-gray-200 rounded mb-2" />
              <div className="h-3 bg-gray-200 rounded w-2/3" />
            </div>
          </Button>
        ))}
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`flex gap-2 ${className}`}>
        {categories.map((category) => {
          const Icon = category.icon;
          const categoryName = (category as any).originalName || category.title;
          const categorySelected = isSelected(categoryName);
          const providerCount = parseInt(category.description.split(' ')[0]) || 0;
          
        return (
          <Button
            key={category.id}
            variant={categorySelected ? 'default' : 'outline'}
            size="sm"
            onClick={category.disabled ? undefined : (multiSelect ? () => handleCategoryClick(categoryName, category.id) : () => handleCategoryNavigation(category.id, providerCount))}
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
        const categoryName = (category as any).originalName || category.title;
        const categorySelected = isSelected(categoryName);
        const providerCount = parseInt(category.description.split(' ')[0]) || 0;

        return (
          <Button
            key={category.id}
            variant={categorySelected ? 'default' : 'outline'}
            className="h-auto p-4 flex flex-col items-center text-center"
            onClick={category.disabled ? undefined : (multiSelect ? () => handleCategoryClick(categoryName, category.id) : () => handleCategoryNavigation(category.id, providerCount))}
            disabled={category.disabled}
          >
            <Icon size={32} className="mb-2" />
            <div>
              <div className="font-semibold text-mobile-base">{category.title}</div>
              <div className="text-sm opacity-75 mt-1">{category.description}</div>
            </div>
            {multiSelect && categorySelected && (
              <div className="absolute top-2 right-2 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center text-white text-xs">✓</div>
            )}
          </Button>
        );
      })}
    </div>
  );
};