import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle, Clock, Phone, Home } from 'lucide-react';

export const SignupSuccess: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-md w-full space-y-6">
          {/* Success Icon */}
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle size={32} className="text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              درخواست ثبت‌نام با موفقیت ارسال شد
            </h1>
            <p className="text-muted-foreground">
              درخواست شما ثبت شد و کارشناس بازرگانی برای بررسی و تایید با شما تماس خواهد گرفت
            </p>
          </div>

          {/* Status Card */}
          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center gap-3">
                <Clock size={20} className="text-amber-500" />
                <div>
                  <h3 className="font-semibold">در انتظار بررسی کارشناس بازرگانی</h3>
                  <p className="text-sm text-muted-foreground">
                    کارشناس بازرگانی ظرف ۲۴ ساعت آینده برای بررسی و تایید هویت شما تماس خواهد گرفت
                  </p>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-medium mb-2">مراحل بعدی:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• بررسی اطلاعات ثبت شده توسط کارشناس بازرگانی</li>
                  <li>• تماس تلفنی برای احراز هویت و تایید نهایی</li>
                  <li>• تایید درخواست و فعال‌سازی در سیستم</li>
                  <li>• نمایش اطلاعات شرکت در سایت برای مشتریان</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Contact Info */}
          <Card>
            <CardContent className="p-6">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Phone size={16} />
                تماس با پشتیبانی
              </h3>
              <p className="text-sm text-muted-foreground mb-2">
                در صورت داشتن سؤال یا نیاز به راهنمایی:
              </p>
              <div className="text-sm space-y-1">
                <p>📞 تلفن: ۰۲۱-۱۲۳۴۵۶۷۸</p>
                <p>📧 ایمیل: support@truckaid.ir</p>
                <p>🕐 ساعات کاری: ۸:۰۰ تا ۲۰:۰۰</p>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="space-y-3">
            <Button
              onClick={() => navigate('/services')}
              className="w-full"
              size="lg"
              variant="hero"
            >
              <Home className="ml-2" size={16} />
              بازگشت به صفحه اصلی
            </Button>
            
            <Button 
              onClick={() => navigate('/contact')}
              variant="outline"
              className="w-full"
            >
              تماس با پشتیبانی
            </Button>
          </div>

          {/* Additional Info */}
          <div className="text-center text-xs text-muted-foreground">
            <p>
              شما در صورت تأیید، یک پیامک حاوی اطلاعات ورود دریافت خواهید کرد
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};