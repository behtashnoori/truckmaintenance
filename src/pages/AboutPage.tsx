import React from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Card, CardContent } from '@/components/ui/card';
import { Truck, Users, Target, Shield, Award, MapPin } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '@/utils/api';
import { convertToPersianNumbers } from '@/utils/persianNumbers';

export const AboutPage: React.FC = () => {
  const { data: aboutContent, isLoading, error } = useQuery({
    queryKey: ['about-content'],
    queryFn: async () => {
      const response = await apiFetch('/api/content/about');
      if (!response.success) {
        throw new Error(response.error || 'خطا در دریافت محتوا');
      }
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header title="درباره ما" />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">در حال بارگذاری...</div>
        </div>
        <Footer />
      </div>
    );
  }

  if (error || !aboutContent) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <Header title="درباره ما" />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center text-red-600">
            خطا در بارگذاری محتوا
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="درباره ما" />
      
      <div className="flex-1 p-6 space-y-6">
        {/* Hero Section */}
        <div className="gradient-hero text-white p-6 rounded-lg text-center">
          <Truck size={48} className="mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">{convertToPersianNumbers(aboutContent.hero_title || 'امداد کامیون')}</h1>
          <p className="opacity-90">
            {convertToPersianNumbers(aboutContent.hero_subtitle || 'پلتفرم جامع خدمات اضطراری و تعمیرات خودروهای سنگین')}
          </p>
        </div>

        {/* Mission */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <Target size={24} className="text-primary mt-1 flex-shrink-0" />
              <div>
                <h2 className="text-lg font-semibold mb-2">ماموریت ما</h2>
                <p className="text-muted-foreground">
                  {convertToPersianNumbers(aboutContent.mission_text || 'هدف ما ارائه سریع‌ترین و مطمئن‌ترین خدمات امداد و تعمیرات برای رانندگان کامیون و خودروهای سنگین در سراسر کشور است. ما معتقدیم که هر راننده‌ای حق دارد در هر زمان و مکان به خدمات با کیفیت دسترسی داشته باشد.')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Team */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <Users size={24} className="text-primary mt-1 flex-shrink-0" />
              <div>
                <h2 className="text-lg font-semibold mb-2">تیم ما</h2>
                <p className="text-muted-foreground">
                  {convertToPersianNumbers(aboutContent.team_text || 'تیم امداد کامیون متشکل از مهندسان، متخصصان فنی و کارشناسان مجرب در زمینه حمل‌ونقل و خدمات خودرویی است. ما با بیش از ۱۰ سال تجربه در این صنعت، به دنبال ایجاد راه‌حلی مدرن و کارآمد برای نیازهای رانندگان هستیم.')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <Shield size={32} className="mx-auto mb-3 text-primary" />
              <h3 className="font-semibold mb-2">امنیت و اعتماد</h3>
              <p className="text-sm text-muted-foreground">
                {convertToPersianNumbers(aboutContent.feature_security || 'همه ارائه‌دهندگان خدمات ما تأیید شده و دارای مجوزهای لازم هستند')}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <MapPin size={32} className="mx-auto mb-3 text-primary" />
              <h3 className="font-semibold mb-2">پوشش سراسری</h3>
              <p className="text-sm text-muted-foreground">
                {convertToPersianNumbers(aboutContent.feature_coverage || 'خدمات در تمام نقاط کشور و جاده‌های اصلی در دسترس است')}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Award size={32} className="mx-auto mb-3 text-primary" />
              <h3 className="font-semibold mb-2">کیفیت بالا</h3>
              <p className="text-sm text-muted-foreground">
                {convertToPersianNumbers(aboutContent.feature_quality || 'استانداردهای سخت‌گیرانه برای انتخاب و ارزیابی ارائه‌دهندگان')}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Truck size={32} className="mx-auto mb-3 text-primary" />
              <h3 className="font-semibold mb-2">تخصص در کامیون</h3>
              <p className="text-sm text-muted-foreground">
                {convertToPersianNumbers(aboutContent.feature_expertise || 'متمرکز بر نیازهای خاص خودروهای سنگین و تجاری')}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Statistics */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-4 text-center">آمار و اعداد</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary">۵۰۰+</div>
                <div className="text-sm text-muted-foreground">ارائه‌دهنده فعال</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-primary">۱۰,۰۰۰+</div>
                <div className="text-sm text-muted-foreground">خدمت ارائه‌شده</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-primary">۳۱</div>
                <div className="text-sm text-muted-foreground">استان تحت پوشش</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-primary">۲۴/۷</div>
                <div className="text-sm text-muted-foreground">پشتیبانی</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Version Info */}
        <Card>
          <CardContent className="p-4">
            <div className="text-center text-sm text-muted-foreground">
              <p>نسخه ۱.۰.۰ - بهمن ۱۴۰۳</p>
              <p className="mt-1">توسعه داده شده با ❤️ برای رانندگان ایرانی</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};