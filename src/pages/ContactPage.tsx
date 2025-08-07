import React, { useState } from 'react';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Phone, Mail, MapPin, Clock, Send } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { submitContactForm } from '@/lib/api';

export const ContactPage: React.FC = () => {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.email.trim() || !formData.message.trim()) {
      toast({
        title: "خطا",
        description: "لطفاً فیلدهای الزامی را پر کنید",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);
    try {
      await submitContactForm(formData);
      toast({
        title: "پیام ارسال شد",
        description: "پیام شما با موفقیت ارسال شد. در اسرع وقت پاسخ خواهیم داد",
      });
      setFormData({ name: '', email: '', subject: '', message: '' });
    } catch (error) {
      toast({
        title: "خطا در ارسال",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header title="تماس با ما" />
      
      <div className="flex-1 p-6 space-y-6">
        {/* Contact Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <Phone size={32} className="mx-auto mb-3 text-primary" />
              <h3 className="font-semibold mb-2">تلفن پشتیبانی</h3>
              <p className="text-sm text-muted-foreground mb-2">۲۴ ساعته در خدمت شما</p>
              <a href="tel:+982112345678" className="text-primary font-medium">
                ۰۲۱-۱۲۳۴۵۶۷۸
              </a>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4 text-center">
              <Mail size={32} className="mx-auto mb-3 text-primary" />
              <h3 className="font-semibold mb-2">ایمیل</h3>
              <p className="text-sm text-muted-foreground mb-2">پاسخ در کمتر از ۲۴ ساعت</p>
              <a href="mailto:support@truckaid.ir" className="text-primary font-medium">
                support@truckaid.ir
              </a>
            </CardContent>
          </Card>
        </div>

        {/* Office Address */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <MapPin size={24} className="text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold mb-2">دفتر مرکزی</h3>
                <p className="text-muted-foreground mb-2">
                  تهران، خیابان ولیعصر، بالاتر از تقاطع پارک‌ساعی، 
                  پلاک ۱۲۳۴، طبقه ۵، واحد ۱۰
                </p>
                <p className="text-sm text-muted-foreground">
                  کد پستی: ۱۹۱۵۷-۴۴۴۱۱
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Working Hours */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <Clock size={24} className="text-primary mt-1 flex-shrink-0" />
              <div>
                <h3 className="font-semibold mb-3">ساعات کاری</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>شنبه تا پنج‌شنبه:</span>
                    <span className="font-medium">۸:۰۰ - ۲۰:۰۰</span>
                  </div>
                  <div className="flex justify-between">
                    <span>جمعه:</span>
                    <span className="font-medium">۱۰:۰۰ - ۱۸:۰۰</span>
                  </div>
                  <div className="flex justify-between">
                    <span>خدمات اضطراری:</span>
                    <span className="font-medium text-primary">۲۴ ساعته</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Contact Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Send size={20} />
              ارسال پیام
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">نام و نام خانوادگی *</Label>
                  <Input
                    id="name"
                    placeholder="نام خود را وارد کنید"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email">ایمیل *</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="example@email.com"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="ltr text-right"
                    required
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="subject">موضوع</Label>
                <Input
                  id="subject"
                  placeholder="موضوع پیام شما"
                  value={formData.subject}
                  onChange={(e) => handleInputChange('subject', e.target.value)}
                />
              </div>
              
              <div>
                <Label htmlFor="message">پیام *</Label>
                <Textarea
                  id="message"
                  placeholder="پیام خود را بنویسید..."
                  rows={5}
                  value={formData.message}
                  onChange={(e) => handleInputChange('message', e.target.value)}
                  required
                />
              </div>
              
              <Button 
                type="submit"
                disabled={isSubmitting}
                className="w-full"
                size="lg"
                variant="hero"
              >
                <Send className="ml-2" size={16} />
                {isSubmitting ? 'در حال ارسال...' : 'ارسال پیام'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Quick Help */}
        <Card>
          <CardContent className="p-6">
            <h3 className="font-semibold mb-3">سؤالات متداول</h3>
            <div className="space-y-3 text-sm">
              <div>
                <h4 className="font-medium">چگونه ارائه‌دهنده خدمات شوم؟</h4>
                <p className="text-muted-foreground">از منوی اصلی گزینه "ثبت‌نام ارائه‌دهنده" را انتخاب کنید.</p>
              </div>
              <div>
                <h4 className="font-medium">آیا خدمات شبانه‌روزی است؟</h4>
                <p className="text-muted-foreground">بله، خدمات اضطراری ۲۴ ساعته در دسترس است.</p>
              </div>
              <div>
                <h4 className="font-medium">چگونه کیفیت خدمات کنترل می‌شود؟</h4>
                <p className="text-muted-foreground">همه ارائه‌دهندگان تأیید شده و بازخوردهای مشتریان بررسی می‌شود.</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Footer />
    </div>
  );
};