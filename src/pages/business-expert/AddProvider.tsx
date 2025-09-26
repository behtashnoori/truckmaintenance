import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { MapPicker } from '@/components/MapPicker';
import { useToast } from '@/hooks/use-toast';
import { Building, MapPin, Phone, User, Save, ArrowLeft } from 'lucide-react';

const SERVICE_CATEGORIES = [
  'تعمیرات موتور',
  'تعمیرات گیربکس',
  'تعمیرات ترمز',
  'تعمیرات سیستم برق',
  'تعمیرات سیستم خنک‌کننده',
  'تعمیرات سیستم سوخت',
  'تعمیرات سیستم اگزوز',
  'تعمیرات سیستم تعلیق',
  'تعمیرات سیستم فرمان',
  'تعمیرات سیستم تایر',
  'تعمیرات سیستم کولر',
  'تعمیرات سیستم گرمایش',
  'سرویس‌های عمومی',
  'تعمیرات تخصصی',
  'سایر'
];

export const AddProvider: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    companyName: '',
    representativeFirstName: '',
    representativeLastName: '',
    address: '',
    phoneMobile: '',
    phoneLandline: '',
    serviceDomain: '',
    latitude: undefined as number | undefined,
    longitude: undefined as number | undefined,
    isActive: true
  });

  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (field: string, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
    const required = ['companyName', 'representativeFirstName', 'representativeLastName', 'address', 'phoneMobile', 'serviceDomain'];
    const missing = required.filter(field => !formData[field as keyof typeof formData]);
    
    if (missing.length > 0) {
      toast({
        title: "خطا",
        description: `لطفاً فیلدهای الزامی را پر کنید: ${missing.join(', ')}`,
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

    return true;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/business-expert/providers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast({
          title: 'ارائه‌دهنده اضافه شد',
          description: 'ارائه‌دهنده با موفقیت به سیستم اضافه شد.',
        });
        navigate('/business-expert/dashboard');
      } else {
        const error = await response.json();
        throw new Error(error.message || 'خطا در اضافه کردن ارائه‌دهنده');
      }
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
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/business-expert/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            بازگشت به داشبورد
          </Button>
          
          <h1 className="text-3xl font-bold text-foreground mb-2">
            اضافه کردن ارائه‌دهنده جدید
          </h1>
          <p className="text-muted-foreground">
            اطلاعات ارائه‌دهنده خدمات را وارد کنید
          </p>
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
                  placeholder="نام مجموعه"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="representativeFirstName">نام نماینده *</Label>
                  <Input
                    id="representativeFirstName"
                    value={formData.representativeFirstName}
                    onChange={(e) => handleInputChange('representativeFirstName', e.target.value)}
                    placeholder="نام"
                  />
                </div>
                <div>
                  <Label htmlFor="representativeLastName">نام خانوادگی نماینده *</Label>
                  <Input
                    id="representativeLastName"
                    value={formData.representativeLastName}
                    onChange={(e) => handleInputChange('representativeLastName', e.target.value)}
                    placeholder="نام خانوادگی"
                  />
                </div>
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
                >
                  <SelectTrigger>
                    <SelectValue placeholder="انتخاب حوزه خدمات" />
                  </SelectTrigger>
                  <SelectContent>
                    {SERVICE_CATEGORIES.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
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
    </div>
  );
};
