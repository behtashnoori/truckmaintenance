import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { PageNavigation } from '@/components/PageNavigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { MapPicker } from '@/components/MapPicker';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';
import BusinessExpertLayout from '@/components/business-expert/BusinessExpertLayout';
import { Building, MapPin, Phone, User, Save } from 'lucide-react';

interface Category {
  id: number;
  name: string;
}

export const AddProvider: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    companyName: '',
    address: '',
    phoneMobile: '',
    phoneLandline: '',
    serviceDomain: '',
    latitude: undefined as number | undefined,
    longitude: undefined as number | undefined,
    isActive: true
  });

  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);

  // Load categories from API
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await apiFetch('/api/public/categories');
        setCategories(response.data || []);
      } catch (error) {
        console.error('Error loading categories:', error);
        toast({ 
          title: 'خطا در دریافت دسته‌بندی‌ها', 
          description: 'نتوانستیم دسته‌بندی‌ها را بارگذاری کنیم', 
          variant: 'destructive' 
        });
      } finally {
        setCategoriesLoading(false);
      }
    };

    loadCategories();
  }, [toast]);

  const handleInputChange = (field: string, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
    const required = ['companyName', 'address', 'phoneMobile', 'serviceDomain'];
    const missing = required.filter(field => !formData[field as keyof typeof formData]);
    
    if (missing.length > 0) {
      toast({
        title: "خطا",
        description: `لطفاً فیلدهای الزامی را پر کنید`,
        variant: "destructive",
      });
      return false;
    }

    if (formData.latitude === undefined || formData.longitude === undefined) {
      toast({
        title: "خطا",
        description: "لطفاً موقعیت را روی نقشه مشخص کنید.",
        variant: "destructive",
      });
      return false;
    }
    
    // Validate phone number format
    const phonePattern = /^09\d{9}$/;
    if (!phonePattern.test(formData.phoneMobile)) {
      toast({
        title: "خطا",
        description: "شماره موبایل باید با فرمت 09xxxxxxxxx باشد",
        variant: "destructive",
      });
      return false;
    }

    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await apiFetch('/api/business-expert/providers', {
        method: 'POST',
        body: JSON.stringify(formData),
      });

      toast({
        title: 'ارائه‌دهنده اضافه شد',
        description: 'ارائه‌دهنده با موفقیت به سیستم اضافه شد.',
      });
      navigate('/business-expert/providers');
    } catch (error) {
      console.error('Error adding provider:', error);
      toast({
        title: 'خطا',
        description: 'خطا در اضافه کردن ارائه‌دهنده. لطفاً دوباره تلاش کنید.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <BusinessExpertLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              اضافه کردن ارائه‌دهنده جدید
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              اطلاعات ارائه‌دهنده خدمات را وارد کنید
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* فرم اطلاعات */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building size={20} />
                اطلاعات ارائه‌دهنده
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="companyName">نام مجموعه *</Label>
                <Input
                  id="companyName"
                  value={formData.companyName}
                  onChange={(e) => handleInputChange('companyName', e.target.value)}
                  placeholder="مثال: تعمیرگاه رضا"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  نام شرکت یا مجموعه ارائه‌دهنده خدمات
                </p>
              </div>

              <div>
                <Label htmlFor="address">آدرس *</Label>
                <Textarea
                  id="address"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  placeholder="نشانی کامل"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="phoneMobile">شماره موبایل *</Label>
                  <Input
                    id="phoneMobile"
                    value={formData.phoneMobile}
                    onChange={(e) => handleInputChange('phoneMobile', e.target.value)}
                    placeholder="09123456789"
                    className="ltr text-right"
                  />
                </div>
                <div>
                  <Label htmlFor="phoneLandline">تلفن ثابت</Label>
                  <Input
                    id="phoneLandline"
                    value={formData.phoneLandline}
                    onChange={(e) => handleInputChange('phoneLandline', e.target.value)}
                    placeholder="021XXXXXXX"
                    className="ltr text-right"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="serviceDomain">حوزه ارائه خدمات *</Label>
                <Select
                  value={formData.serviceDomain}
                  onValueChange={(value) => handleInputChange('serviceDomain', value)}
                  disabled={categoriesLoading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={categoriesLoading ? "در حال بارگذاری..." : "انتخاب حوزه خدمات"} />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.name}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {categories.length === 0 && !categoriesLoading && (
                  <p className="text-sm text-muted-foreground mt-1">
                    هیچ دسته‌بندی‌ای یافت نشد
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="isActive"
                  checked={formData.isActive}
                  onCheckedChange={(checked) => handleInputChange('isActive', checked)}
                />
                <Label htmlFor="isActive">فعال در سیستم</Label>
              </div>
            </CardContent>
          </Card>

          {/* نقشه و دکمه‌ها */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin size={20} />
                  موقعیت روی نقشه
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <MapPicker
                  lat={formData.latitude}
                  lon={formData.longitude}
                  onChange={(lat, lon) => {
                    handleInputChange('latitude', lat);
                    handleInputChange('longitude', lon);
                  }}
                />
                <p className="text-sm text-muted-foreground">
                  با کلیک روی نقشه، پین را جابه‌جا کنید.
                </p>
                {formData.latitude !== undefined && formData.longitude !== undefined && (
                  <p className="text-xs text-muted-foreground">
                    lat: {formData.latitude.toFixed(6)} - lon: {formData.longitude.toFixed(6)}
                  </p>
                )}
              </CardContent>
            </Card>

            <div className="flex gap-4">
              <Button
                onClick={handleSubmit}
                disabled={isLoading}
                className="flex-1"
                size="lg"
              >
                <Save className="w-4 h-4 mr-2" />
                {isLoading ? 'در حال ذخیره...' : 'ذخیره ارائه‌دهنده'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </BusinessExpertLayout>
  );
};
