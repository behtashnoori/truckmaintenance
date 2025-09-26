import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import BusinessExpertLayout from '@/components/business-expert/BusinessExpertLayout';
import { 
  CheckCircle, 
  XCircle, 
  Phone, 
  MapPin, 
  Building, 
  User, 
  Clock,
  ArrowLeft,
  MessageCircle,
  FileText
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ApplicationData {
  id: number;
  company_name: string;
  representative_first_name: string;
  representative_last_name: string;
  address: string;
  phone_mobile: string;
  phone_landline?: string;
  service_domain: string;
  latitude: number;
  longitude: number;
  status: string;
  created_at: string;
  reviewed_by?: number;
  reviewed_at?: string;
  review_notes?: string;
  is_approved: boolean;
}

export default function ApplicationReview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [application, setApplication] = useState<ApplicationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [reviewNotes, setReviewNotes] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    loadApplication();
  }, [id]);

  const loadApplication = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await apiFetch(`/business-expert/applications/${id}`);
      
      // Mock data
      setApplication({
        id: parseInt(id || '1'),
        company_name: 'شرکت تعمیرات سنگین آریا',
        representative_first_name: 'علی',
        representative_last_name: 'احمدی',
        address: 'تهران، خیابان آزادی، پلاک 123',
        phone_mobile: '09123456789',
        phone_landline: '02112345678',
        service_domain: 'تعمیرات موتور',
        latitude: 35.6892,
        longitude: 51.3890,
        status: 'pending',
        created_at: '2024-01-15T10:30:00Z',
        is_approved: false
      });
    } catch (error) {
      toast({
        title: "خطا در بارگذاری",
        description: "نتوانستیم اطلاعات درخواست را بارگذاری کنیم",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setIsProcessing(true);
    try {
      // TODO: Replace with actual API call
      // await apiFetch(`/business-expert/applications/${id}/approve`, {
      //   method: 'POST',
      //   body: JSON.stringify({ notes: reviewNotes })
      // });
      
      toast({
        title: "درخواست تایید شد",
        description: "درخواست با موفقیت تایید و شرکت در سیستم فعال شد",
      });
      
      navigate('/business-expert/dashboard');
    } catch (error) {
      toast({
        title: "خطا در تایید",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!reviewNotes.trim()) {
      toast({
        title: "یادداشت الزامی است",
        description: "لطفاً دلیل رد درخواست را بنویسید",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    try {
      // TODO: Replace with actual API call
      // await apiFetch(`/business-expert/applications/${id}/reject`, {
      //   method: 'POST',
      //   body: JSON.stringify({ notes: reviewNotes })
      // });
      
      toast({
        title: "درخواست رد شد",
        description: "درخواست رد شد و به متقاضی اطلاع داده خواهد شد",
      });
      
      navigate('/business-expert/dashboard');
    } catch (error) {
      toast({
        title: "خطا در رد درخواست",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading) {
    return (
      <BusinessExpertLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">در حال بارگذاری...</p>
          </div>
        </div>
      </BusinessExpertLayout>
    );
  }

  if (!application) {
    return (
      <BusinessExpertLayout>
        <div className="text-center py-8">
          <p className="text-gray-600 dark:text-gray-400">درخواست مورد نظر یافت نشد</p>
          <Button onClick={() => navigate('/business-expert/dashboard')} className="mt-4">
            بازگشت به داشبورد
          </Button>
        </div>
      </BusinessExpertLayout>
    );
  }

  return (
    <BusinessExpertLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/business-expert/dashboard')}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              بازگشت
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                بررسی درخواست ثبت‌نام
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                بررسی و تایید درخواست شرکت: {application.company_name}
              </p>
            </div>
          </div>
          <Badge variant={application.status === 'pending' ? 'secondary' : 'default'}>
            {application.status === 'pending' ? 'در انتظار بررسی' : application.status}
          </Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Application Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Company Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="w-5 h-5" />
                  اطلاعات شرکت
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">نام شرکت</Label>
                    <p className="text-lg font-semibold">{application.company_name}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">حوزه خدمات</Label>
                    <p className="text-lg font-semibold">{application.service_domain}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">نام نماینده</Label>
                    <p className="text-lg">{application.representative_first_name} {application.representative_last_name}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">تاریخ ثبت درخواست</Label>
                    <p className="text-lg">{new Date(application.created_at).toLocaleDateString('fa-IR')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  اطلاعات تماس
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">شماره موبایل</Label>
                    <p className="text-lg font-mono">{application.phone_mobile}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">تلفن ثابت</Label>
                    <p className="text-lg font-mono">{application.phone_landline || 'ثبت نشده'}</p>
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">آدرس</Label>
                  <p className="text-lg">{application.address}</p>
                </div>
              </CardContent>
            </Card>

            {/* Location */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  موقعیت مکانی
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">عرض جغرافیایی</Label>
                    <p className="font-mono">{application.latitude.toFixed(6)}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">طول جغرافیایی</Label>
                    <p className="font-mono">{application.longitude.toFixed(6)}</p>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
                    نقشه موقعیت در اینجا نمایش داده خواهد شد
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Review Actions */}
          <div className="space-y-6">
            {/* Review Notes */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  یادداشت بررسی
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="reviewNotes">نظرات و یادداشت‌ها</Label>
                  <Textarea
                    id="reviewNotes"
                    placeholder="نظرات خود را درباره این درخواست بنویسید..."
                    value={reviewNotes}
                    onChange={(e) => setReviewNotes(e.target.value)}
                    rows={6}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Action Buttons */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="w-5 h-5" />
                  تصمیم‌گیری
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <Button
                    onClick={handleApprove}
                    disabled={isProcessing}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="mr-2 h-4 w-4" />
                    {isProcessing ? 'در حال تایید...' : 'تایید درخواست'}
                  </Button>
                  
                  <Button
                    onClick={handleReject}
                    disabled={isProcessing}
                    variant="destructive"
                    className="w-full"
                  >
                    <XCircle className="mr-2 h-4 w-4" />
                    {isProcessing ? 'در حال رد...' : 'رد درخواست'}
                  </Button>
                </div>

                <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
                  <p>• پس از تایید، شرکت در سایت نمایش داده می‌شود</p>
                  <p>• پس از رد، به متقاضی اطلاع داده می‌شود</p>
                  <p>• یادداشت‌ها برای متقاضی ارسال می‌شود</p>
                </div>
              </CardContent>
            </Card>

            {/* Contact Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="w-5 h-5" />
                  تماس با متقاضی
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => window.open(`tel:${application.phone_mobile}`)}
                >
                  <Phone className="mr-2 h-4 w-4" />
                  تماس با {application.representative_first_name}
                </Button>
                
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => window.open(`sms:${application.phone_mobile}`)}
                >
                  <MessageCircle className="mr-2 h-4 w-4" />
                  ارسال پیامک
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </BusinessExpertLayout>
  );
}

