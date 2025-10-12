import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { PageNavigation } from '@/components/PageNavigation';
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
  FileText,
  FileCheck,
  AlertTriangle,
  Info
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';

interface ApplicationData {
  id: number;
  company_name: string;
  representative_first_name: string;
  representative_last_name: string;
  address: string;
  phone_mobile: string;
  phone_landline?: string;
  service_categories: string[];
  latitude: number;
  longitude: number;
  status: string;
  created_at: string;
  reviewed_by?: number;
  reviewed_at?: string;
  review_notes?: string;
  is_approved: boolean;
  reapplication_count?: number;
  fuzzy_match_warning?: boolean;
  similar_company_names?: string;
}

export default function ApplicationReview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [application, setApplication] = useState<ApplicationData | null>(null);
  const [applications, setApplications] = useState<ApplicationData[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewNotes, setReviewNotes] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (id) {
      loadApplication();
    } else {
      loadApplications();
    }
  }, [id]);

  const loadApplication = async () => {
    try {
      // Get real data from API
      const response = await apiFetch(`/api/business-expert/applications/${id}`);
      setApplication(response.data || response);
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

  const loadApplications = async () => {
    try {
      // Get all pending applications
      const response = await apiFetch('/api/business-expert/applications?status=pending');
      setApplications(response.data || response.items || []);
    } catch (error) {
      toast({
        title: "خطا در بارگذاری",
        description: "نتوانستیم لیست درخواست‌ها را بارگذاری کنیم",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setIsProcessing(true);
    try {
      await apiFetch(`/api/business-expert/applications/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ notes: reviewNotes })
      });
      
      toast({
        title: "درخواست تایید شد",
        description: "درخواست با موفقیت تایید و شرکت در سیستم فعال شد",
      });
      
      navigate('/business-expert/applications');
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
      await apiFetch(`/api/business-expert/applications/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ notes: reviewNotes })
      });
      
      toast({
        title: "درخواست رد شد",
        description: "درخواست رد شد و به متقاضی اطلاع داده خواهد شد",
      });
      
      navigate('/business-expert/applications');
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

  const handleQuickApprove = async (appId: number) => {
    try {
      await apiFetch(`/api/business-expert/applications/${appId}/approve`, {
        method: 'POST',
        body: JSON.stringify({ notes: 'تایید سریع توسط کارشناس' })
      });
      
      toast({
        title: "درخواست تایید شد",
        description: "درخواست با موفقیت تایید شد",
      });
      
      // Reload applications list
      loadApplications();
    } catch (error) {
      toast({
        title: "خطا در تایید",
        description: "لطفاً دوباره تلاش کنید",
        variant: "destructive",
      });
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

  // Show applications list if no specific ID
  if (!id) {
    return (
      <BusinessExpertLayout>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                درخواست‌های در انتظار بررسی
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                بررسی و تایید درخواست‌های ثبت‌نام جدید
              </p>
            </div>
            <Button onClick={() => navigate('/business-expert/dashboard')}>
              بازگشت به داشبورد
            </Button>
          </div>

          {applications.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <FileCheck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">هیچ درخواستی یافت نشد</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  در حال حاضر هیچ درخواست در انتظار بررسی وجود ندارد
                </p>
                <Button onClick={() => navigate('/business-expert/dashboard')}>
                  بازگشت به داشبورد
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {applications.map((app) => (
                <Card key={app.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <CardTitle>{app.company_name}</CardTitle>
                          {app.fuzzy_match_warning && (
                            <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-300 dark:bg-yellow-900/20 dark:text-yellow-400">
                              <AlertTriangle className="w-3 h-3 mr-1" />
                              نام مشابه
                            </Badge>
                          )}
                          {app.reapplication_count && app.reapplication_count > 1 && (
                            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300 dark:bg-blue-900/20 dark:text-blue-400">
                              <Info className="w-3 h-3 mr-1" />
                              درخواست {app.reapplication_count}م
                            </Badge>
                          )}
                        </div>
                        <CardDescription>
                          نماینده: {app.representative_first_name} {app.representative_last_name}
                        </CardDescription>
                      </div>
                      <Badge variant="secondary">جدید</Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {(app.fuzzy_match_warning || app.similar_company_names) && (
                      <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md">
                        <div className="flex items-start gap-2">
                          <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                          <div className="flex-1">
                            <p className="text-sm font-medium text-yellow-800 dark:text-yellow-300">
                              هشدار: نام شرکت مشابه
                            </p>
                            {app.similar_company_names && (
                              <p className="text-xs text-yellow-700 dark:text-yellow-400 mt-1">
                                شباهت با: {app.similar_company_names}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      <div>
                        <span className="font-medium">تلفن:</span>
                        <p className="text-muted-foreground">{app.phone_mobile}</p>
                      </div>
                      <div className="col-span-2">
                        <span className="font-medium">حوزه‌های خدمات:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {app.service_categories && app.service_categories.map((cat) => (
                            <span key={cat} className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                              {cat}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <span className="font-medium">آدرس:</span>
                        <p className="text-muted-foreground">{app.address}</p>
                      </div>
                      <div>
                        <span className="font-medium">تاریخ ثبت:</span>
                        <p className="text-muted-foreground">
                          {new Date(app.created_at).toLocaleDateString('fa-IR')}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => navigate(`/business-expert/review/${app.id}`)}
                      >
                        بررسی جزئیات
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleQuickApprove(app.id)}
                      >
                        تایید سریع
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </BusinessExpertLayout>
    );
  }

  if (!application) {
    return (
      <BusinessExpertLayout>
        <div className="text-center py-8">
          <p className="text-gray-600 dark:text-gray-400">درخواست مورد نظر یافت نشد</p>
          <Button onClick={() => navigate('/business-expert/applications')} className="mt-4">
            بازگشت به لیست درخواست‌ها
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
              onClick={() => navigate('/business-expert/applications')}
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
            {/* Warning Indicators */}
            {(application.fuzzy_match_warning || application.reapplication_count && application.reapplication_count > 1) && (
              <div className="space-y-3">
                {application.fuzzy_match_warning && (
                  <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-yellow-800 dark:text-yellow-300 mb-1">
                          هشدار: نام شرکت مشابه شناسایی شد
                        </h3>
                        <p className="text-sm text-yellow-700 dark:text-yellow-400">
                          نام این شرکت شباهت زیادی به شرکت‌های دیگر در سیستم دارد. لطفاً دقت کنید که این درخواست تکراری نباشد.
                        </p>
                        {application.similar_company_names && (
                          <p className="text-sm text-yellow-700 dark:text-yellow-400 mt-2">
                            <span className="font-medium">شرکت‌های مشابه:</span> {application.similar_company_names}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
                
                {application.reapplication_count && application.reapplication_count > 1 && (
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-start gap-3">
                      <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <h3 className="font-semibold text-blue-800 dark:text-blue-300 mb-1">
                          این {application.reapplication_count}مین بار درخواست این متقاضی است
                        </h3>
                        <p className="text-sm text-blue-700 dark:text-blue-400">
                          این متقاضی قبلاً {application.reapplication_count - 1} بار درخواست ثبت‌نام کرده است.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            
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
                  <div className="md:col-span-2">
                    <Label className="text-sm font-medium text-gray-600">حوزه‌های خدمات</Label>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {application.service_categories && application.service_categories.map((cat) => (
                        <span key={cat} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 font-semibold">
                          {cat}
                        </span>
                      ))}
                    </div>
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
            
            {/* Navigation */}
            <PageNavigation position="bottom" variant="floating" homePath="/business-expert/dashboard" />
          </div>
        </div>
      </div>
    </BusinessExpertLayout>
  );
}

