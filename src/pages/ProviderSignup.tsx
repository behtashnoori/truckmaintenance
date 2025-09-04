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
import { ServiceCategory, VehicleType, requestOTP, verifyOTP, createProvider, createCompany } from '@/lib/api';
import { Phone, Building, Radius, Clock, Truck, Bus } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export const ProviderSignup: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Step management
  const [currentStep, setCurrentStep] =
    useState<'phone' | 'otp' | 'company' | 'details'>('phone');
  
  // Phone & OTP
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [authToken, setAuthToken] = useState<string | null>(null);
  
  // Business details
  const [companyName, setCompanyName] = useState('');
  const steps: Array<'phone' | 'otp' | 'company' | 'details'> = [
    'phone',
    'otp',
    'company',
    'details',
  ];
  const currentIndex = steps.indexOf(currentStep);
  const [selectedCategories, setSelectedCategories] = useState<ServiceCategory[]>([]);
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
      const res = await requestOTP(phone);
      if (res.success) {
        setCurrentStep('otp');
        toast({
          title: "کد تأیید ارسال شد",
          description: "کد ۶ رقمی به شماره شما پیامک شد",
        });
      } else {
        let description = "لطفاً دوباره تلاش کنید";
        if (res.error?.includes("OTP recently requested")) {
          description = "کد تأیید قبلاً ارسال شده است. لطفاً لحظاتی بعد دوباره تلاش کنید";
        }
        toast({
          title: "خطا در ارسال کد",
          description,
          variant: "destructive",
        });
      }
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
      const res = await verifyOTP(phone, otp);
      if (res.success && res.data) {
        setAuthToken(res.data.token);
        setCurrentStep('company');
        toast({
          title: "شماره تأیید شد",
          description: "نام شرکت خود را وارد کنید",
        });
      } else {
        throw new Error(res.error || '');
      }
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
      const res = await createCompany({ name: companyName, phone }, authToken!);
      if (res.success) {
        setCurrentStep('details');
      } else {
        throw new Error(res.error || '');
      }
    } catch (error) {
      toast({
        title: "خطا در ثبت شرکت",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
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

    if (selectedCategories.length === 0) {
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
      const res = await createProvider({
        name: companyName,
        phone,
        radius_km: parseInt(radius),
        categories: selectedCategories,
        is_24_7: is24_7,
        vehicle_types: selectedVehicleTypes
      }, authToken!);
      if (res.success) {
        navigate('/signup/success');
      } else {
        throw new Error(res.error || '');
      }
    } catch (error) {
      toast({
        title: "خطا در ثبت‌نام",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCategoryToggle = (category: ServiceCategory) => {
    setSelectedCategories(prev => 
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
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
                <CardHeader>
                  <CardTitle>خدمات ارائه‌شده</CardTitle>
                </CardHeader>
                <CardContent>
                  <CategorySelector
                    selectedCategory={selectedCategories[0]}
                    onCategorySelect={handleCategoryToggle}
                    multiSelect={true}
                    selectedCategories={selectedCategories}
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
                  selectedCategories.length === 0 ||
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