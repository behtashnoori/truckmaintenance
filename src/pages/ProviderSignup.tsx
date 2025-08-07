import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp';
import { CategorySelector } from '@/components/CategorySelector';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ServiceCategory, requestOTP, verifyOTP, createProvider } from '@/lib/api';
import { MapPin, Phone, Building, Radius } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface LocationData {
  lat: number;
  lon: number;
  address: string;
}

export const ProviderSignup: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Step management
  const [currentStep, setCurrentStep] = useState<'phone' | 'otp' | 'details'>('phone');
  
  // Phone & OTP
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Business details
  const [businessName, setBusinessName] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<ServiceCategory[]>([]);
  const [location, setLocation] = useState<LocationData | null>(null);
  const [radius, setRadius] = useState('50');

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
      setCurrentStep('details');
      toast({
        title: "شماره تأیید شد",
        description: "اکنون اطلاعات کسب‌وکار خود را وارد کنید",
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

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      toast({
        title: "خطا",
        description: "مرورگر شما از موقعیت‌یابی پشتیبانی نمی‌کند",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
          address: `عرض: ${position.coords.latitude.toFixed(6)}, طول: ${position.coords.longitude.toFixed(6)}`
        });
        setIsLoading(false);
        toast({
          title: "موقعیت تأیید شد",
          description: "موقعیت فعلی شما ثبت شد",
        });
      },
      (error) => {
        setIsLoading(false);
        toast({
          title: "خطا در دریافت موقعیت",
          description: "لطفاً دسترسی به موقعیت را مجاز کنید",
          variant: "destructive",
        });
      }
    );
  };

  const handleSubmit = async () => {
    if (!businessName.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً نام کسب‌وکار را وارد کنید",
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

    if (!location) {
      toast({
        title: "خطا",
        description: "لطفاً موقعیت خود را مشخص کنید",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      await createProvider({
        name: businessName,
        phone,
        location: {
          lat: location.lat,
          lon: location.lon
        },
        radius_km: parseInt(radius),
        categories: selectedCategories
      });
      
      navigate('/signup/success');
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

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="ثبت‌نام ارائه‌دهنده" />
      
      <div className="flex-1 p-6">
        <div className="max-w-md mx-auto space-y-6">
          {/* Progress Indicator */}
          <div className="flex justify-center space-x-2 mb-6">
            <div className={`w-3 h-3 rounded-full ${currentStep === 'phone' ? 'bg-primary' : currentStep === 'otp' || currentStep === 'details' ? 'bg-primary' : 'bg-muted'}`} />
            <div className={`w-3 h-3 rounded-full ${currentStep === 'otp' ? 'bg-primary' : currentStep === 'details' ? 'bg-primary' : 'bg-muted'}`} />
            <div className={`w-3 h-3 rounded-full ${currentStep === 'details' ? 'bg-primary' : 'bg-muted'}`} />
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

          {/* Details Step */}
          {currentStep === 'details' && (
            <div className="space-y-6">
              {/* Business Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building size={20} />
                    اطلاعات کسب‌وکار
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="businessName">نام کسب‌وکار</Label>
                    <Input
                      id="businessName"
                      placeholder="نام شرکت یا کارگاه"
                      value={businessName}
                      onChange={(e) => setBusinessName(e.target.value)}
                    />
                  </div>
                </CardContent>
              </Card>

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
                </CardContent>
              </Card>

              {/* Location */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin size={20} />
                    موقعیت و شعاع فعالیت
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!location ? (
                    <Button 
                      onClick={handleGetCurrentLocation}
                      disabled={isLoading}
                      variant="outline"
                      className="w-full"
                    >
                      <MapPin className="ml-2" size={16} />
                      {isLoading ? 'در حال دریافت موقعیت...' : 'دریافت موقعیت فعلی'}
                    </Button>
                  ) : (
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">موقعیت ثبت‌شده:</p>
                      <p className="text-sm font-mono">{location.address}</p>
                    </div>
                  )}
                  
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

              {/* Submit */}
              <Button 
                onClick={handleSubmit}
                disabled={isLoading || !businessName.trim() || selectedCategories.length === 0 || !location}
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