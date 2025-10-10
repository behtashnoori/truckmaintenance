import React from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { PageNavigation } from '@/components/PageNavigation';
import { Card, CardContent } from '@/components/ui/card';
import { Shield, Lock, Eye, Database, UserCheck } from 'lucide-react';

export const PrivacyPolicy: React.FC = () => {
  const lastUpdated = "۱۵ بهمن ۱۴۰۳";

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="سیاست حفظ حریم خصوصی" />
      
      <div className="flex-1 p-6 space-y-6">
        {/* Navigation */}
        <PageNavigation position="top" variant="inline" />
        
        {/* Header */}
        <Card>
          <CardContent className="p-6 text-center">
            <Shield size={48} className="mx-auto mb-4 text-primary" />
            <h1 className="text-xl font-bold mb-2">سیاست حفظ حریم خصوصی</h1>
            <p className="text-muted-foreground">
              آخرین بروزرسانی: {lastUpdated}
            </p>
          </CardContent>
        </Card>

        {/* Introduction */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <UserCheck size={20} />
              مقدمه
            </h2>
            <p className="text-muted-foreground leading-relaxed">
              در امداد کامیون، حفظ حریم خصوصی و امنیت اطلاعات شخصی شما برای ما بسیار مهم است. 
              این سیاست توضیح می‌دهد که چگونه اطلاعات شما را جمع‌آوری، استفاده، ذخیره و محافظت می‌کنیم. 
              با استفاده از خدمات ما، شما با این سیاست موافقت می‌کنید.
            </p>
          </CardContent>
        </Card>

        {/* Information Collection */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Database size={20} />
              اطلاعات جمع‌آوری‌شده
            </h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2">اطلاعات شخصی</h3>
                <ul className="text-sm text-muted-foreground space-y-1 mr-4">
                  <li>• نام و نام خانوادگی</li>
                  <li>• شماره تلفن همراه</li>
                  <li>• آدرس ایمیل</li>
                  <li>• اطلاعات کسب‌وکار (برای ارائه‌دهندگان)</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-medium mb-2">اطلاعات موقعیت مکانی</h3>
                <ul className="text-sm text-muted-foreground space-y-1 mr-4">
                  <li>• موقعیت جغرافیایی فعلی (با اجازه شما)</li>
                  <li>• سابقه جستجوهای مکانی</li>
                  <li>• منطقه فعالیت (برای ارائه‌دهندگان)</li>
                </ul>
              </div>

              <div>
                <h3 className="font-medium mb-2">اطلاعات فنی</h3>
                <ul className="text-sm text-muted-foreground space-y-1 mr-4">
                  <li>• نوع مرورگر و دستگاه</li>
                  <li>• آدرس IP</li>
                  <li>• زمان استفاده از خدمات</li>
                  <li>• صفحات بازدید شده</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Usage of Information */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Eye size={20} />
              نحوه استفاده از اطلاعات
            </h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• ارائه و بهبود خدمات درخواستی شما</p>
              <p>• یافتن نزدیک‌ترین ارائه‌دهندگان خدمات</p>
              <p>• برقراری ارتباط برای پشتیبانی و خدمات</p>
              <p>• تأیید هویت و جلوگیری از سوءاستفاده</p>
              <p>• بهبود امنیت پلتفرم</p>
              <p>• ارسال اطلاعیه‌های مرتبط با خدمات</p>
              <p>• تجزیه و تحلیل آماری برای بهبود خدمات</p>
              <p>• رعایت قوانین و مقررات</p>
            </div>
          </CardContent>
        </Card>

        {/* Information Sharing */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">اشتراک‌گذاری اطلاعات</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium mb-2 text-green-600">اطلاعاتی که به اشتراک می‌گذاریم:</h3>
                <ul className="text-sm text-muted-foreground space-y-1 mr-4">
                  <li>• اطلاعات عمومی ارائه‌دهندگان (نام، تلفن، آدرس)</li>
                  <li>• موقعیت تقریبی برای یافتن خدمات نزدیک</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-medium mb-2 text-red-600">اطلاعاتی که به اشتراک نمی‌گذاریم:</h3>
                <ul className="text-sm text-muted-foreground space-y-1 mr-4">
                  <li>• اطلاعات شخصی بدون اجازه شما</li>
                  <li>• موقعیت دقیق بدون ضرورت</li>
                  <li>• سابقه جستجوها و فعالیت‌های شخصی</li>
                  <li>• اطلاعات مالی یا حساس</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Data Security */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Lock size={20} />
              امنیت اطلاعات
            </h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• رمزگذاری اطلاعات حین انتقال و ذخیره‌سازی</p>
              <p>• محدود کردن دسترسی به اطلاعات شخصی</p>
              <p>• نظارت مداوم بر امنیت سیستم‌ها</p>
              <p>• بکاپ‌گیری منظم و ایمن</p>
              <p>• آموزش کارکنان در زمینه حفظ حریم خصوصی</p>
              <p>• استفاده از پروتکل‌های امنیتی پیشرفته</p>
            </div>
          </CardContent>
        </Card>

        {/* User Rights */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">حقوق کاربران</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• <strong>دسترسی:</strong> مشاهده اطلاعات شخصی ذخیره‌شده</p>
              <p>• <strong>اصلاح:</strong> درخواست اصلاح اطلاعات نادرست</p>
              <p>• <strong>حذف:</strong> درخواست حذف اطلاعات شخصی</p>
              <p>• <strong>محدودیت:</strong> محدود کردن پردازش اطلاعات</p>
              <p>• <strong>انتقال:</strong> دریافت کپی از اطلاعات شخصی</p>
              <p>• <strong>اعتراض:</strong> اعتراض به پردازش اطلاعات</p>
            </div>
          </CardContent>
        </Card>

        {/* Cookies and Tracking */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">کوکی‌ها و ردیابی</h2>
            <div className="space-y-3 text-sm text-muted-foreground">
              <p>• استفاده از کوکی‌های ضروری برای عملکرد سایت</p>
              <p>• کوکی‌های تجزیه و تحلیل برای بهبود خدمات</p>
              <p>• عدم استفاده از کوکی‌های تبلیغاتی</p>
              <p>• امکان کنترل کوکی‌ها از طریق تنظیمات مرورگر</p>
            </div>
          </CardContent>
        </Card>

        {/* Changes to Policy */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">تغییرات سیاست</h2>
            <p className="text-sm text-muted-foreground">
              این سیاست ممکن است بروزرسانی شود. تغییرات مهم از طریق ایمیل یا اطلاعیه در سایت به شما اطلاع داده خواهد شد. 
              استفاده مداوم از خدمات پس از تغییرات، به منزله پذیرش سیاست جدید است.
            </p>
          </CardContent>
        </Card>

        {/* Contact Information */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-lg font-semibold mb-3">تماس با ما</h2>
            <p className="text-sm text-muted-foreground mb-3">
              برای سؤالات مربوط به حریم خصوصی:
            </p>
            <div className="text-sm space-y-1">
              <p>📧 ایمیل: privacy@truckaid.ir</p>
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