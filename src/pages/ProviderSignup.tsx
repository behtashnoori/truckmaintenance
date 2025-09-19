import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { CategorySelector } from '@/components/CategorySelector';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ServiceCategory, VehicleType, requestOTP, verifyOTP } from '@/lib/api';
import { apiFetch } from '@/utils/api';
import { Phone, Building, Radius, Clock, Truck, Bus } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export const ProviderSignup: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const categoryLabels: Record<ServiceCategory, string> = {
    roadside: 'خدمات جاده‌ای',
    tire: 'لاستیک و رینگ',
    recovery: 'امداد و حادثه',
    oil: 'فروش روغن و فیلتر',
  };

  const vehicleLabels: Record<VehicleType, string> = {
    truck: 'کامیون',
    semi: 'تریلی',
    bus: 'اتوبوس',
  };
  
  // Step management
  const [currentStep, setCurrentStep] =
    useState<'phone' | 'otp' | 'company' | 'details'>('phone');
  
  // Phone & OTP
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Business details
  const [companyName, setCompanyName] = useState('');
  const steps: Array<'phone' | 'otp' | 'company' | 'details'> = [
    'phone',
    'otp',
    'company',
    'details',
  ];
  const currentIndex = steps.indexOf(currentStep);
  const [selectedCategory, setSelectedCategory] = useState<ServiceCategory | undefined>(undefined);
  const [radius, setRadius] = useState('50');
  const [is24_7, setIs24_7] = useState(false);
  const [selectedVehicleTypes, setSelectedVehicleTypes] = useState<VehicleType[]>([]);

  const handleSendOTP = async () => {
    if (!phone.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً شماره تلفن را وارد کنید",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      await requestOTP(phone);
      setCurrentStep('otp');
      toast({
        title: "کد تأیید ارسال شد",
        description: "کد ۶ رقمی به شماره شما پیامک شد",
      });
    } catch (error) {
      toast({
        title: "خطا در ارسال کد",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (otp.length !== 6) {
      toast({
        title: "خطا",
        description: "لطفاً کد ۶ رقمی را کامل وارد کنید",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      await verifyOTP(phone, otp);
      localStorage.setItem('provider_phone', phone);
      setCurrentStep('company');
      toast({
        title: "شماره تأیید شد",
        description: "نام شرکت خود را وارد کنید",
      });
    } catch (error) {
      toast({
        title: "کد نامعتبر",
        description: "لطفاً کد صحیح را وارد کنید",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCompanySubmit = async () => {
    if (!companyName.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً نام شرکت را وارد کنید",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const storedPhone = localStorage.getItem('provider_phone') || '';
      const name = companyName.trim();
      if (!storedPhone) {
        throw new Error('شماره تلفن یافت نشد؛ مرحله قبل را کامل کنید');
      }
      const json = await apiFetch<{ id: number }>('/api/signup/company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: storedPhone, name }),
      });
      localStorage.setItem('provider_company_id', String(json.id));
      setCurrentStep('details');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'لطفاً دوباره تلاش کنید';
      toast({
        title: 'خطا در ثبت شرکت',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!companyName.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً نام شرکت را وارد کنید",
        variant: "destructive",
      });
      return;
    }

    if (!selectedCategory) {
      toast({
        title: "خطا",
        description: "لطفاً حداقل یک دسته خدمات انتخاب کنید",
        variant: "destructive",
      });
      return;
    }

    if (selectedVehicleTypes.length === 0) {
      toast({
        title: "خطا",
        description: "لطفاً حداقل یک نوع وسیله انتخاب کنید",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const companyId = localStorage.getItem('provider_company_id');
      if (!companyId) {
        throw new Error('شناسه شرکت یافت نشد؛ لطفاً مراحل قبلی را کامل کنید');
      }

      const typeOfService = selectedCategory ? categoryLabels[selectedCategory] : '';
      const radiusValue = Number.parseInt(radius, 10);
      const workingHours = is24_7 ? 'شبانه‌روزی' : 'غیر شبانه‌روزی';
      const vehicleType = selectedVehicleTypes
        .map(vehicle => vehicleLabels[vehicle])
        .join(', ');

      await apiFetch(`/api/signup/company/${companyId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type_of_service: typeOfService,
          radius_of_activity: Number.isNaN(radiusValue) ? undefined : radiusValue,
          working_hours: workingHours,
          vehicle_type: vehicleType,
          date: new Date().toISOString(),
        }),
      });

      navigate('/signup/success');
    } catch (error) {
      toast({
        title: "خطا در ثبت‌نام",
        description:
          error instanceof Error ? error.message : "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCategorySelect = (category: ServiceCategory) => {
    setSelectedCategory(prev => (prev === category ? undefined : category));
  };

  const handleVehicleTypeToggle = (vehicleType: VehicleType) => {
    setSelectedVehicleTypes(prev => 
      prev.includes(vehicleType)
        ? prev.filter(v => v !== vehicleType)
        : [...prev, vehicleType]
    );
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="ثبت‌نام ارائه‌دهنده" />
      
      <div className="flex-1 p-6">
        <div className="max-w-md mx-auto space-y-6">
          {/* Progress Indicator */}
          <div className="flex justify-center space-x-2 mb-6">
            {steps.map((step, idx) => (
              <div
                key={step}
                className={`w-3 h-3 rounded-full ${
                  idx <= currentIndex ? 'bg-primary' : 'bg-muted'
                }`}
              />
            ))}
          </div>

          {/* Phone Step */}
          {currentStep === 'phone' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone size={20} />
                  تأیید شماره تلفن
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="phone">شماره موبایل</Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="09123456789"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="ltr text-right"
                    maxLength={11}
                  />
                </div>
                <Button 
                  onClick={handleSendOTP}
                  disabled={isLoading || !phone.trim()}
                  className="w-full"
                  size="lg"
                >
                  {isLoading ? 'در حال ارسال...' : 'ارسال کد تأیید'}
                </Button>
              </CardContent>
            </Card>
          )}

          {/* OTP Step */}
          {currentStep === 'otp' && (
            <Card>
              <CardHeader>
                <CardTitle>وارد کردن کد تأیید</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  کد ۶ رقمی ارسال شده به {phone} را وارد کنید
                </p>
                <div className="flex justify-center">
                  <InputOTP value={otp} onChange={setOtp} maxLength={6}>
                    <InputOTPGroup>
                      <InputOTPSlot index={0} />
                      <InputOTPSlot index={1} />
                      <InputOTPSlot index={2} />
                      <InputOTPSlot index={3} />
                      <InputOTPSlot index={4} />
                      <InputOTPSlot index={5} />
                    </InputOTPGroup>
                  </InputOTP>
                </div>
                <Button 
                  onClick={handleVerifyOTP}
                  disabled={isLoading || otp.length !== 6}
                  className="w-full"
                  size="lg"
                >
                  {isLoading ? 'در حال تأیید...' : 'تأیید کد'}
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => setCurrentStep('phone')}
                  className="w-full"
                >
                  تغییر شماره تلفن
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Company Step */}
          {currentStep === 'company' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building size={20} />
                  ثبت نام شرکت
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="companyName">نام شرکت</Label>
                  <Input
                    id="companyName"
                    placeholder="نام شرکت"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                  />
                </div>
                <Button
                  onClick={handleCompanySubmit}
                  disabled={isLoading || !companyName.trim()}
                  className="w-full"
                  size="lg"
                >
                  ادامه
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Details Step */}
          {currentStep === 'details' && (
            <div className="space-y-6">
              {/* Services */}
              <Card>
                <CardHeader className="items-center">
                  <CardTitle>خدمات ارائه‌شده</CardTitle>
                </CardHeader>
                <CardContent>
                  <CategorySelector
                    selectedCategory={selectedCategory}
                    onCategorySelect={handleCategorySelect}
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    حداقل یک دسته خدمات انتخاب کنید
                  </p>
                </CardContent>
              </Card>

              {/* Service Radius */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Radius size={20} />
                    شعاع فعالیت
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="radius" className="flex items-center gap-2">
                      <Radius size={16} />
                      شعاع فعالیت (کیلومتر)
                    </Label>
                    <Input
                      id="radius"
                      type="number"
                      placeholder="50"
                      value={radius}
                      onChange={(e) => setRadius(e.target.value)}
                      min="1"
                      max="200"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Service Hours */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock size={20} />
                    ساعات کاری
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="is_24_7">سرویس‌دهی ۲۴ ساعته</Label>
                      <p className="text-sm text-muted-foreground">آیا در تمام ساعات شبانه‌روز خدمات ارائه می‌دهید؟</p>
                    </div>
                    <Switch
                      id="is_24_7"
                      checked={is24_7}
                      onCheckedChange={setIs24_7}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Vehicle Types */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Truck size={20} />
                    نوع وسایل نقلیه قابل سرویس
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="vehicle-truck"
                        checked={selectedVehicleTypes.includes('truck')}
                        onCheckedChange={() => handleVehicleTypeToggle('truck')}
                      />
                      <Label htmlFor="vehicle-truck" className="flex items-center gap-2 cursor-pointer">
                        <Truck size={16} />
                        کامیون
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="vehicle-semi"
                        checked={selectedVehicleTypes.includes('semi')}
                        onCheckedChange={() => handleVehicleTypeToggle('semi')}
                      />
                      <Label htmlFor="vehicle-semi" className="flex items-center gap-2 cursor-pointer">
                        <Truck size={16} />
                        تریلی
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="vehicle-bus"
                        checked={selectedVehicleTypes.includes('bus')}
                        onCheckedChange={() => handleVehicleTypeToggle('bus')}
                      />
                      <Label htmlFor="vehicle-bus" className="flex items-center gap-2 cursor-pointer">
                        <Bus size={16} />
                        اتوبوس
                      </Label>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    حداقل یک نوع وسیله انتخاب کنید
                  </p>
                </CardContent>
              </Card>

              {/* Submit */}
              <Button
                onClick={handleSubmit}
                disabled={
                  isLoading ||
                  !selectedCategory ||
                  selectedVehicleTypes.length === 0
                }
                className="w-full"
                size="lg"
                variant="hero"
              >
                {isLoading ? 'در حال ثبت‌نام...' : 'ثبت‌نام نهایی'}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};