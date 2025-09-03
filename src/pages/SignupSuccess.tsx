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
              ثبت‌نام با موفقیت انجام شد
            </h1>
            <p className="text-muted-foreground">
              اطلاعات شما دریافت شد و در حال بررسی است
            </p>
          </div>

          {/* Status Card */}
          <Card>
            <CardContent className="p-6 space-y-4">
              <div className="flex items-center gap-3">
                <Clock size={20} className="text-amber-500" />
                <div>
                  <h3 className="font-semibold">در انتظار تأیید</h3>
                  <p className="text-sm text-muted-foreground">
                    تیم ما اطلاعات شما را در ۲۴ ساعت آینده بررسی خواهد کرد
                  </p>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-medium mb-2">مراحل بعدی:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• بررسی اطلاعات و مدارک ارسالی</li>
                  <li>• تماس تلفنی برای تأیید نهایی</li>
                  <li>• فعال‌سازی حساب کاربری</li>
                  <li>• ارسال اطلاعات ورود به سامانه</li>
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