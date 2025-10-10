import React from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { PageNavigation } from '@/components/PageNavigation';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Scale, AlertTriangle, Shield, Users } from 'lucide-react';

export const TermsOfService: React.FC = () => {
  const lastUpdated = "۱۵ بهمن ۱۴۰۳";

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="شرایط و قوانین استفاده" />
      
      <div className="flex-1 p-6 space-y-6">
        {/* Navigation */}
        <PageNavigation position="top" variant="inline" />
        
        {/* Header */}
        <Card>
          <CardContent className="p-6 text-center">
            <FileText size={48} className="mx-auto mb-4 text-primary" />
            <h1 className="text-xl font-bold mb-2">شرایط و قوانین استفاده</h1>
            <p className="text-muted-foreground">
              آخرین بروزرسانی: {lastUpdated}
            </p>
          </CardContent>
        </Card>

        {/* Introduction */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Scale size={20} />
              مقدمه
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              این شرایط و قوانین ("شرایط") استفاده از پلتفرم امداد کامیون ("سرویس") را تنظیم می‌کند. 
              با دسترسی یا استفاده از سرویس، شما با این شرایط موافقت می‌کنید. 
              اگر با هر بخشی از این شرایط موافق نیستید، لطفاً از سرویس استفاده نکنید.
            </p>
          </CardContent>
        </Card>

        {/* Service Description */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">توصیف خدمات</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>امداد کامیون پلتفرمی است که:</p>
              <ul className="space-y-1 mr-4">
                <li>• ارائه‌دهندگان خدمات خودروهای سنگین را معرفی می‌کند</li>
                <li>• جستجوی خدمات بر اساس موقعیت جغرافیایی را فراهم می‌کند</li>
                <li>• ابزاری برای ارتباط بین رانندگان و ارائه‌دهندگان است</li>
                <li>• اطلاعات تماس و موقعیت ارائه‌دهندگان را نمایش می‌دهد</li>
              </ul>
              <p className="text-amber-600 font-medium">
                توجه: ما واسط معرفی هستیم و مسئولیت مستقیم کیفیت خدمات ارائه‌شده توسط شخص ثالث را نداریم.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* User Responsibilities */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Users size={20} />
              مسئولیت‌های کاربران
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">همه کاربران:</h3>
                <ul className="text-sm text-muted-foreground space-y-1 mr-4">
                  <li>• ارائه اطلاعات صحیح و به‌روز</li>
                  <li>• رعایت قوانین و مقررات کشور</li>
                  <li>• احترام به سایر کاربران</li>
                  <li>• عدم سوءاستفاده از سرویس</li>
                  <li>• حفظ امنیت اطلاعات ورود</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-medium mb-2">ارائه‌دهندگان خدمات:</h3>
                <ul className="text-sm text-muted-foreground space-y-1 mr-4">
                  <li>• داشتن مجوزهای قانونی لازم</li>
                  <li>• ارائه خدمات با کیفیت مناسب</li>
                  <li>• پاسخگویی مناسب به مشتریان</li>
                  <li>• بروزرسانی اطلاعات تماس و دسترسی</li>
                  <li>• رعایت استانداردهای ایمنی</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Prohibited Uses */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <AlertTriangle size={20} />
              موارد ممنوع
            </h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>استفاده از سرویس برای موارد زیر ممنوع است:</p>
              <ul className="space-y-1 mr-4">
                <li>• فعالیت‌های غیرقانونی یا مخرب</li>
                <li>• ارسال اطلاعات نادرست یا گمراه‌کننده</li>
                <li>• سوءاستفاده از اطلاعات سایر کاربران</li>
                <li>• تلاش برای نفوذ یا آسیب به سیستم</li>
                <li>• ارسال محتوای نامناسب یا توهین‌آمیز</li>
                <li>• استفاده تجاری بدون مجوز</li>
                <li>• تکثیر یا کپی‌برداری غیرمجاز</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Liability Limitations */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">محدودیت مسئولیت</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                <h3 className="font-medium text-amber-800 mb-2">توجه مهم:</h3>
                <p className="text-amber-700">
                  امداد کامیون صرفاً پلتفرم معرفی است و مسئولیت کیفیت، قیمت، زمان‌بندی یا سایر جنبه‌های خدمات ارائه‌شده توسط شخص ثالث را نمی‌پذیرد.
                </p>
              </div>
              
              <p>ما مسئول موارد زیر نیستیم:</p>
              <ul className="space-y-1 mr-4">
                <li>• کیفیت خدمات ارائه‌شده توسط ارائه‌دهندگان</li>
                <li>• مشکلات یا اختلافات بین کاربران</li>
                <li>• خسارات ناشی از استفاده از خدمات شخص ثالث</li>
                <li>• قطع موقت یا دائمی سرویس</li>
                <li>• از دست رفتن اطلاعات یا داده‌ها</li>
                <li>• خطاهای فنی یا نقص‌های سیستم</li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Privacy and Data */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Shield size={20} />
              حریم خصوصی و اطلاعات
            </h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• جمع‌آوری و استفاده از اطلاعات طبق سیاست حریم خصوصی</p>
              <p>• حفظ امنیت اطلاعات شخصی کاربران</p>
              <p>• عدم فروش یا واگذاری اطلاعات به اشخاص ثالث</p>
              <p>• استفاده از اطلاعات صرفاً برای بهبود خدمات</p>
              <p>• حق کاربران برای دسترسی و اصلاح اطلاعات</p>
            </div>
          </CardContent>
        </Card>

        {/* Service Availability */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">در دسترس بودن سرویس</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• تلاش برای ارائه سرویس ۲۴ ساعته و ۷ روز هفته</p>
              <p>• امکان قطع موقت برای نگهداری و بروزرسانی</p>
              <p>• عدم تضمین عملکرد بدون وقفه</p>
              <p>• اطلاع‌رسانی پیشین در صورت قطع برنامه‌ریزی‌شده</p>
            </div>
          </CardContent>
        </Card>

        {/* Modifications */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">تغییرات شرایط</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• حق تغییر این شرایط در هر زمان محفوظ است</p>
              <p>• اطلاع‌رسانی تغییرات مهم از طریق سایت یا ایمیل</p>
              <p>• استفاده مداوم پس از تغییرات به منزله پذیرش است</p>
              <p>• بررسی منظم شرایط توسط کاربران توصیه می‌شود</p>
            </div>
          </CardContent>
        </Card>

        {/* Termination */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">خاتمه استفاده</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• حق تعلیق یا حذف حساب کاربری در صورت نقض شرایط</p>
              <p>• امکان حذف داوطلبانه حساب توسط کاربر</p>
              <p>• حفظ اطلاعات ضروری طبق قوانین کشور</p>
              <p>• ادامه اعتبار شرایط پس از خاتمه استفاده</p>
            </div>
          </CardContent>
        </Card>

        {/* Governing Law */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">قانون حاکم</h2>
            <p className="text-sm text-muted-foreground">
              این شرایط طبق قوانین جمهوری اسلامی ایران تفسیر و اجرا می‌شود. 
              هرگونه اختلاف در محاکم صالح تهران رسیدگی خواهد شد.
            </p>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">تماس با ما</h2>
            <p className="text-sm text-muted-foreground mb-3">
              برای سؤالات مربوط به شرایط استفاده:
            </p>
            <div className="text-sm space-y-1">
              <p>📧 ایمیل: legal@truckaid.ir</p>
              <p>📞 تلفن: ۰۲۱-۱۲۳۴۵۶۷۸</p>
              <p>📍 آدرس: تهران، خیابان ولیعصر، پلاک ۱۲۳۴</p>
            </div>
          </CardContent>
        </Card>
        
        {/* Bottom Navigation */}
        <PageNavigation position="bottom" variant="floating" />
      </div>

      <Footer />
    </div>
  );
};