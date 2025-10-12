import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { CategorySelector } from '@/components/CategorySelector';
import { PageNavigation } from '@/components/PageNavigation';
import { Header } from '@/components/Header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ServiceCategory, submitProviderApplication, ApiError, ApiWarning } from '@/lib/api';
import { Building, MapPin, Phone, User, FileText, CheckCircle, ArrowRight, AlertTriangle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { MapPicker } from '@/components/MapPicker';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export const ProviderSignup: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  
  // Form state
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState<'info' | 'location' | 'review'>('info');
  
  // Company information
  const [companyName, setCompanyName] = useState('');
  const [repFirstName, setRepFirstName] = useState('');
  const [repLastName, setRepLastName] = useState('');
  const [address, setAddress] = useState('');
  const [phoneMobile, setPhoneMobile] = useState('');
  const [phoneLandline, setPhoneLandline] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  
  // Location
  const [latitude, setLatitude] = useState<number | undefined>(undefined);
  const [longitude, setLongitude] = useState<number | undefined>(undefined);

  const handleCategorySelect = (categories: string[]) => {
    setSelectedCategories(categories);
  };

  const validateStep1 = () => {
    if (!companyName.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً نام شرکت را وارد کنید",
        variant: "destructive",
      });
      return false;
    }
    if (!repFirstName.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً نام نماینده را وارد کنید",
        variant: "destructive",
      });
      return false;
    }
    if (!repLastName.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً نام خانوادگی نماینده را وارد کنید",
        variant: "destructive",
      });
      return false;
    }
    if (!address.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً آدرس را وارد کنید",
        variant: "destructive",
      });
      return false;
    }
    if (!phoneMobile.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً شماره موبایل را وارد کنید",
        variant: "destructive",
      });
      return false;
    }
    if (!selectedCategories || selectedCategories.length === 0) {
      toast({
        title: "خطا",
        description: "لطفاً حداقل یک حوزه خدمات را انتخاب کنید",
        variant: "destructive",
      });
      return false;
    }
    return true;
  };

  const validateStep2 = () => {
    if (latitude === undefined || longitude === undefined) {
      toast({
        title: "خطا",
        description: "لطفاً موقعیت خود را روی نقشه مشخص کنید",
        variant: "destructive",
      });
      return false;
    }
    return true;
  };

  const handleNextStep = () => {
    if (currentStep === 'info' && validateStep1()) {
      setCurrentStep('location');
    } else if (currentStep === 'location' && validateStep2()) {
      setCurrentStep('review');
    }
  };

  const handlePrevStep = () => {
    if (currentStep === 'location') {
      setCurrentStep('info');
    } else if (currentStep === 'review') {
      setCurrentStep('location');
    }
  };

  const handleSubmit = async () => {
    if (!validateStep1() || !validateStep2()) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await submitProviderApplication({
        companyName,
        representativeFirstName: repFirstName,
        representativeLastName: repLastName,
        address,
        phoneMobile,
        phoneLandline: phoneLandline || undefined,
        serviceCategories: selectedCategories,
        latitude: latitude!,
        longitude: longitude!,
      });
      
      if (response.success) {
        // Show success message
        toast({
          title: "درخواست ثبت شد",
          description: response.message || "درخواست شما با موفقیت ثبت شد. کارشناس بازرگانی ظرف 24 ساعت آینده برای بررسی و تایید با شما تماس خواهد گرفت.",
        });

        // Show fuzzy match warning if present
        if (response.warning) {
          toast({
            title: response.warning.message,
            description: response.warning.note,
            variant: "default",
          });
        }
        
        navigate('/signup/success');
      } else {
        // Handle different error codes
        const error = response.error;
        
        if (typeof error === 'object' && error !== null) {
          const apiError = error as ApiError;
          
          switch (apiError.code) {
            case 'DUPLICATE_PHONE':
              toast({
                title: "شماره تکراری",
                description: (
                  <div className="space-y-2">
                    <p>{apiError.message}</p>
                    <p className="text-sm">{apiError.action}</p>
                    {apiError.support_contact && (
                      <p className="text-sm font-semibold">شماره پشتیبانی: {apiError.support_contact}</p>
                    )}
                    {apiError.details && (
                      <p className="text-xs text-muted-foreground">{apiError.details}</p>
                    )}
                  </div>
                ),
                variant: "destructive",
                duration: 10000, // Show for 10 seconds
              });
              break;
              
            case 'RATE_LIMIT_EXCEEDED':
              toast({
                title: "تعداد درخواست بیش از حد",
                description: `${apiError.message} (حداکثر ${apiError.max_attempts} درخواست در ساعت)`,
                variant: "destructive",
                duration: 8000,
              });
              break;
              
            case 'INVALID_PHONE':
              toast({
                title: "شماره موبایل نامعتبر",
                description: apiError.message,
                variant: "destructive",
              });
              break;
              
            case 'INVALID_COMPANY_NAME':
              toast({
                title: "نام شرکت نامعتبر",
                description: apiError.message,
                variant: "destructive",
              });
              break;
              
            case 'NETWORK_ERROR':
              toast({
                title: "خطای ارتباط",
                description: apiError.message,
                variant: "destructive",
              });
              break;
              
            default:
              toast({
                title: "خطا در ثبت درخواست",
                description: apiError.message || "لطفاً دوباره تلاش کنید",
                variant: "destructive",
              });
          }
        } else {
          // Handle string error
          toast({
            title: "خطا در ثبت درخواست",
            description: typeof error === 'string' ? error : "لطفاً دوباره تلاش کنید",
            variant: "destructive",
          });
        }
      }
    } catch (error) {
      toast({
        title: "خطا در ثبت درخواست",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const steps = [
    { id: 'info', title: 'اطلاعات شرکت', icon: Building },
    { id: 'location', title: 'موقعیت مکانی', icon: MapPin },
    { id: 'review', title: 'بررسی نهایی', icon: CheckCircle }
  ];

  const currentStepIndex = steps.findIndex(step => step.id === currentStep);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="ثبت‌نام ارائه‌دهنده خدمات" />
      
      <div className="flex-1 p-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Progress Steps */}
          <div className="flex justify-center space-x-4 mb-8">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = index === currentStepIndex;
              const isCompleted = index < currentStepIndex;
              
              return (
                <div key={step.id} className="flex flex-col items-center space-y-2">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isCompleted ? 'bg-green-500 text-white' :
                    isActive ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
                  }`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`text-sm font-medium ${
                    isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Step 1: Company Information */}
          {currentStep === 'info' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="w-5 h-5" />
                  اطلاعات شرکت
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label htmlFor="companyName">نام شرکت/مجموعه *</Label>
                  <Input
                    id="companyName"
                    placeholder="نام شرکت یا مجموعه"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="repFirstName">نام نماینده *</Label>
                    <Input
                      id="repFirstName"
                      placeholder="نام"
                      value={repFirstName}
                      onChange={(e) => setRepFirstName(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="repLastName">نام خانوادگی نماینده *</Label>
                    <Input
                      id="repLastName"
                      placeholder="نام خانوادگی"
                      value={repLastName}
                      onChange={(e) => setRepLastName(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="address">آدرس کامل *</Label>
                  <Input
                    id="address"
                    placeholder="نشانی کامل شرکت"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="phoneMobile">شماره موبایل *</Label>
                    <Input
                      id="phoneMobile"
                      type="tel"
                      placeholder="09123456789"
                      value={phoneMobile}
                      onChange={(e) => setPhoneMobile(e.target.value)}
                      className="ltr text-right"
                      maxLength={11}
                    />
                  </div>
                  <div>
                    <Label htmlFor="phoneLandline">تلفن ثابت</Label>
                    <Input
                      id="phoneLandline"
                      type="tel"
                      placeholder="02112345678"
                      value={phoneLandline}
                      onChange={(e) => setPhoneLandline(e.target.value)}
                      className="ltr text-right"
                    />
                  </div>
                </div>

                <div>
                  <Label>حوزه‌های خدمات *</Label>
                  <CategorySelector
                    multiSelect={true}
                    selectedCategories={selectedCategories}
                    onMultiSelect={handleCategorySelect}
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    یک یا چند حوزه خدمات را انتخاب کنید (می‌توانید در چند حوزه فعالیت داشته باشید)
                  </p>
                  {selectedCategories.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="text-sm font-medium">حوزه‌های انتخاب شده:</span>
                      {selectedCategories.map((cat) => (
                        <span key={cat} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                          {cat}
                          <button
                            onClick={() => handleCategorySelect(selectedCategories.filter(c => c !== cat))}
                            className="mr-2 hover:text-green-600"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <Button 
                  onClick={handleNextStep} 
                  className="w-full" 
                  size="lg"
                  disabled={!companyName.trim() || !repFirstName.trim() || !repLastName.trim() || !address.trim() || !phoneMobile.trim() || selectedCategories.length === 0}
                >
                  ادامه به مرحله بعد
                  <ArrowRight className="mr-2 h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Location */}
          {currentStep === 'location' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  موقعیت مکانی
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label>موقعیت روی نقشه *</Label>
                  <MapPicker 
                    lat={latitude} 
                    lon={longitude} 
                    onChange={(lat, lon) => { 
                      setLatitude(lat); 
                      setLongitude(lon); 
                    }} 
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    با کلیک روی نقشه، موقعیت دقیق شرکت خود را مشخص کنید
                  </p>
                  {latitude !== undefined && longitude !== undefined && (
                    <p className="text-xs text-muted-foreground mt-2">
                      مختصات: {latitude.toFixed(6)}, {longitude.toFixed(6)}
                    </p>
                  )}
                </div>

                <div className="flex gap-4">
                  <Button 
                    onClick={handlePrevStep} 
                    variant="outline" 
                    className="flex-1"
                  >
                    مرحله قبل
                  </Button>
                  <Button 
                    onClick={handleNextStep} 
                    className="flex-1"
                    disabled={latitude === undefined || longitude === undefined}
                  >
                    ادامه
                    <ArrowRight className="mr-2 h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Review */}
          {currentStep === 'review' && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  بررسی نهایی
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    <h3 className="font-semibold text-blue-800 dark:text-blue-200">فرآیند بررسی</h3>
                  </div>
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    پس از ارسال درخواست، کارشناس بازرگانی ظرف 24 ساعت آینده برای بررسی و تایید هویت شما تماس خواهد گرفت.
                  </p>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold">خلاصه اطلاعات:</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">نام شرکت:</span>
                      <p className="text-muted-foreground">{companyName}</p>
                    </div>
                    <div>
                      <span className="font-medium">نماینده:</span>
                      <p className="text-muted-foreground">{repFirstName} {repLastName}</p>
                    </div>
                    <div>
                      <span className="font-medium">شماره تماس:</span>
                      <p className="text-muted-foreground">{phoneMobile}</p>
                    </div>
                    <div className="md:col-span-2">
                      <span className="font-medium">حوزه‌های خدمات:</span>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {selectedCategories.map((cat) => (
                          <span key={cat} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                            {cat}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="md:col-span-2">
                      <span className="font-medium">آدرس:</span>
                      <p className="text-muted-foreground">{address}</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4">
                  <Button 
                    onClick={handlePrevStep} 
                    variant="outline" 
                    className="flex-1"
                  >
                    مرحله قبل
                  </Button>
                  <Button 
                    onClick={handleSubmit} 
                    className="flex-1"
                    disabled={isLoading}
                  >
                    {isLoading ? 'در حال ارسال...' : 'ارسال درخواست'}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
          
          {/* Navigation */}
          <PageNavigation position="bottom" variant="floating" className="mt-6" />
        </div>
      </div>
    </div>
  );
};