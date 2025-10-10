import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PageNavigation } from '@/components/PageNavigation';
import AdminLayout from '@/components/admin/AdminLayout';
import { Download, FileText, BarChart3, TrendingUp, Users, Building, Calendar } from 'lucide-react';
import { apiFetch } from '@/utils/api';

interface ReportData {
  period: string;
  total_applications: number;
  approved_applications: number;
  rejected_applications: number;
  pending_applications: number;
  total_companies: number;
  active_companies: number;
  total_providers: number;
  category_stats: Array<{
    category: string;
    count: number;
    percentage: number;
  }>;
  monthly_stats: Array<{
    month: string;
    applications: number;
    approvals: number;
  }>;
}

export default function Reports() {
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('month');
  const [reportType, setReportType] = useState('summary');

  useEffect(() => {
    loadReportData();
  }, [period]);

  const loadReportData = async () => {
    try {
      setLoading(true);
      const response = await apiFetch(`/api/admin/reports?period=${period}&type=${reportType}`);
      setReportData(response);
    } catch (err) {
      console.error('Error loading report data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'pdf' | 'excel') => {
    try {
      const response = await apiFetch(`/api/admin/reports/export?period=${period}&format=${format}`, {
        method: 'POST'
      });
      
      // Create download link
      const blob = new Blob([response], { 
        type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${period}_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error exporting report:', err);
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">در حال بارگذاری...</div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">گزارش‌ها و آمار</h1>
            <p className="text-muted-foreground">
              مشاهده آمار و گزارش‌های تفصیلی سیستم مدیریت ارائه‌دهندگان خدمات
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => handleExport('pdf')}>
              <FileText className="h-4 w-4 mr-2" />
              دانلود PDF
            </Button>
            <Button variant="outline" onClick={() => handleExport('excel')}>
              <Download className="h-4 w-4 mr-2" />
              دانلود Excel
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>تنظیمات گزارش</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">بازه زمانی</label>
                <Select value={period} onValueChange={setPeriod}>
                  <SelectTrigger>
                    <SelectValue placeholder="انتخاب بازه زمانی" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="week">هفته جاری</SelectItem>
                    <SelectItem value="month">ماه جاری</SelectItem>
                    <SelectItem value="quarter">سه ماهه جاری</SelectItem>
                    <SelectItem value="year">سال جاری</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">نوع گزارش</label>
                <Select value={reportType} onValueChange={setReportType}>
                  <SelectTrigger>
                    <SelectValue placeholder="انتخاب نوع گزارش" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="summary">خلاصه</SelectItem>
                    <SelectItem value="detailed">تفصیلی</SelectItem>
                    <SelectItem value="comparative">مقایسه‌ای</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {reportData && (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">کل درخواست‌ها</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.total_applications}</div>
                  <p className="text-xs text-muted-foreground">
                    +{reportData.approved_applications} تأیید شده
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">نرخ تأیید</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {reportData.total_applications > 0 
                      ? Math.round((reportData.approved_applications / reportData.total_applications) * 100)
                      : 0}%
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {reportData.pending_applications} در انتظار
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">کل شرکت‌ها</CardTitle>
                  <Building className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.total_companies}</div>
                  <p className="text-xs text-muted-foreground">
                    {reportData.active_companies} فعال
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">کل ارائه‌دهندگان</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{reportData.total_providers}</div>
                  <p className="text-xs text-muted-foreground">
                    ارائه‌دهندگان فعال
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Category Statistics */}
            <Card>
              <CardHeader>
                <CardTitle>آمار دسته‌بندی‌ها</CardTitle>
                <CardDescription>
                  توزیع درخواست‌ها بر اساس دسته‌بندی خدمات
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reportData.category_stats.map((stat, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-primary" />
                        <span className="font-medium">{stat.category}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-sm text-muted-foreground">{stat.count} درخواست</span>
                        <span className="text-sm font-medium">{stat.percentage}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Monthly Trends */}
            <Card>
              <CardHeader>
                <CardTitle>روند ماهانه</CardTitle>
                <CardDescription>
                  تغییرات درخواست‌ها و تأییدات در ماه‌های مختلف
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reportData.monthly_stats.map((stat, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{stat.month}</span>
                      </div>
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="text-sm text-muted-foreground">درخواست‌ها</div>
                          <div className="font-bold">{stat.applications}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-muted-foreground">تأییدات</div>
                          <div className="font-bold text-green-600">{stat.approvals}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Summary */}
            <Card>
              <CardHeader>
                <CardTitle>خلاصه گزارش</CardTitle>
                <CardDescription>
                  گزارش {period === 'week' ? 'هفته' : period === 'month' ? 'ماه' : period === 'quarter' ? 'سه ماهه' : 'سال'} جاری
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <p>
                    در بازه زمانی انتخاب شده، مجموعاً <strong>{reportData.total_applications}</strong> درخواست ثبت شده است که 
                    از این تعداد <strong>{reportData.approved_applications}</strong> درخواست تأیید، 
                    <strong>{reportData.rejected_applications}</strong> درخواست رد و 
                    <strong>{reportData.pending_applications}</strong> درخواست در انتظار بررسی است.
                  </p>
                  <p>
                    همچنین تعداد <strong>{reportData.total_companies}</strong> شرکت در سیستم ثبت‌نام شده که 
                    از این تعداد <strong>{reportData.active_companies}</strong> شرکت در حال حاضر فعال است.
                  </p>
                  <p>
                    در مجموع <strong>{reportData.total_providers}</strong> ارائه‌دهنده خدمات در سیستم وجود دارد.
                  </p>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        <PageNavigation />
      </div>
    </AdminLayout>
  );
}
