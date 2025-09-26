import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { apiFetch } from '@/utils/api';
import BusinessExpertLayout from '@/components/business-expert/BusinessExpertLayout';
import { 
  TrendingUp, 
  FileCheck, 
  CheckCircle, 
  DollarSign,
  Clock,
  Users,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Upload,
  Building
} from 'lucide-react';

interface DashboardStats {
  pending_reviews: number;
  approved_today: number;
  monthly_revenue: string;
  total_companies: number;
  review_efficiency: number;
  customer_satisfaction: number;
}

interface RecentActivity {
  id: number;
  company_name: string;
  action: string;
  timestamp: string;
  status: 'approved' | 'rejected' | 'pending';
}

export default function BusinessExpertDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [pendingApplications, setPendingApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // TODO: Replace with actual API calls
      // const [statsResponse, activitiesResponse] = await Promise.all([
      //   apiFetch('/business-expert/dashboard'),
      //   apiFetch('/business-expert/activities')
      // ]);
      
      // Mock data for now
      setStats({
        pending_reviews: 8,
        approved_today: 3,
        monthly_revenue: '12.5M',
        total_companies: 156,
        review_efficiency: 85,
        customer_satisfaction: 92
      });

      setRecentActivities([
        {
          id: 1,
          company_name: 'شرکت تعمیرات سنگین آریا',
          action: 'درخواست تایید شد',
          timestamp: '2 ساعت پیش',
          status: 'approved'
        },
        {
          id: 2,
          company_name: 'خدمات اضطراری پارس',
          action: 'در انتظار بررسی',
          timestamp: '4 ساعت پیش',
          status: 'pending'
        },
        {
          id: 3,
          company_name: 'تعمیرگاه ماشین‌آلات',
          action: 'درخواست رد شد',
          timestamp: '6 ساعت پیش',
          status: 'rejected'
        }
      ]);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'rejected':
        return <ArrowDownRight className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getActivityBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="default" className="bg-green-500">تایید شده</Badge>;
      case 'rejected':
        return <Badge variant="destructive">رد شده</Badge>;
      default:
        return <Badge variant="secondary">در انتظار</Badge>;
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

  return (
    <BusinessExpertLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">داشبورد کارشناسی</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              نمای کلی عملکرد و آمار کارشناسی بازرگانی
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Button 
              onClick={() => navigate('/business-expert/review')}
              className="w-full sm:w-auto"
            >
              <FileCheck className="mr-2 h-4 w-4" />
              بررسی درخواست‌ها
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">در انتظار بررسی</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats?.pending_reviews || 0}</div>
              <p className="text-xs text-muted-foreground">
                درخواست‌های جدید
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">تایید امروز</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats?.approved_today || 0}</div>
              <p className="text-xs text-muted-foreground">
                شرکت‌های تایید شده
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">درآمد ماهانه</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.monthly_revenue || '0'}</div>
              <p className="text-xs text-muted-foreground">
                تومان
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کل شرکت‌ها</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_companies || 0}</div>
              <p className="text-xs text-muted-foreground">
                شرکت‌های فعال
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Provider Management Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="h-5 w-5" />
              مدیریت ارائه‌دهندگان
            </CardTitle>
            <CardDescription>
              اضافه کردن و مدیریت ارائه‌دهندگان خدمات
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button
                onClick={() => navigate('/business-expert/providers/add')}
                className="h-20 flex flex-col items-center justify-center gap-2"
                variant="outline"
              >
                <Plus className="h-6 w-6" />
                <span>اضافه کردن دستی</span>
              </Button>
              
              <Button
                onClick={() => navigate('/business-expert/providers/bulk-upload')}
                className="h-20 flex flex-col items-center justify-center gap-2"
                variant="outline"
              >
                <Upload className="h-6 w-6" />
                <span>آپلود انبوه</span>
              </Button>
              
              <Button
                onClick={() => navigate('/business-expert/providers')}
                className="h-20 flex flex-col items-center justify-center gap-2"
                variant="outline"
              >
                <Building className="h-6 w-6" />
                <span>مدیریت موجود</span>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Pending Applications */}
        <Card>
          <CardHeader>
            <CardTitle>درخواست‌های در انتظار بررسی</CardTitle>
            <CardDescription>
              درخواست‌های ثبت‌نام جدید که نیاز به بررسی و تایید دارند
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Mock pending applications */}
              <div className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-semibold">شرکت تعمیرات سنگین آریا</h4>
                    <p className="text-sm text-muted-foreground">نماینده: علی احمدی</p>
                  </div>
                  <Badge variant="secondary">جدید</Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                  <div>
                    <span className="font-medium">تلفن:</span>
                    <p className="text-muted-foreground">09123456789</p>
                  </div>
                  <div>
                    <span className="font-medium">حوزه خدمات:</span>
                    <p className="text-muted-foreground">تعمیرات موتور</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => navigate('/business-expert/review/1')}>
                    بررسی جزئیات
                  </Button>
                  <Button size="sm" variant="outline">
                    تایید سریع
                  </Button>
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-semibold">خدمات اضطراری پارس</h4>
                    <p className="text-sm text-muted-foreground">نماینده: مریم کریمی</p>
                  </div>
                  <Badge variant="secondary">جدید</Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                  <div>
                    <span className="font-medium">تلفن:</span>
                    <p className="text-muted-foreground">09987654321</p>
                  </div>
                  <div>
                    <span className="font-medium">حوزه خدمات:</span>
                    <p className="text-muted-foreground">خدمات اضطراری</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => navigate('/business-expert/review/2')}>
                    بررسی جزئیات
                  </Button>
                  <Button size="sm" variant="outline">
                    تایید سریع
                  </Button>
                </div>
              </div>

              <div className="text-center pt-4">
                <Button variant="outline" onClick={() => navigate('/business-expert/review')}>
                  مشاهده همه درخواست‌ها ({pendingApplications.length || 5})
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>عملکرد بررسی</CardTitle>
              <CardDescription>
                درصد کارایی در بررسی درخواست‌ها
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">کارایی بررسی</span>
                  <span className="text-sm text-muted-foreground">{stats?.review_efficiency || 0}%</span>
                </div>
                <Progress value={stats?.review_efficiency || 0} className="h-2" />
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">رضایت مشتریان</span>
                  <span className="text-sm text-muted-foreground">{stats?.customer_satisfaction || 0}%</span>
                </div>
                <Progress value={stats?.customer_satisfaction || 0} className="h-2" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>فعالیت‌های اخیر</CardTitle>
              <CardDescription>
                آخرین اقدامات انجام شده
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity) => (
                  <div key={activity.id} className="flex items-center space-x-3 rtl:space-x-reverse">
                    <div className="flex-shrink-0">
                      {getActivityIcon(activity.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {activity.company_name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {activity.action} • {activity.timestamp}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      {getActivityBadge(activity.status)}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={() => navigate('/business-expert/activities')}
                >
                  مشاهده همه فعالیت‌ها
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>عملیات سریع</CardTitle>
            <CardDescription>
              دسترسی سریع به مهم‌ترین عملکردها
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Button 
                variant="outline" 
                className="h-auto p-4 flex flex-col items-center space-y-2"
                onClick={() => navigate('/business-expert/review')}
              >
                <FileCheck className="h-6 w-6" />
                <span>بررسی درخواست‌ها</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto p-4 flex flex-col items-center space-y-2"
                onClick={() => navigate('/business-expert/approval')}
              >
                <CheckCircle className="h-6 w-6" />
                <span>تایید شرکت‌ها</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto p-4 flex flex-col items-center space-y-2"
                onClick={() => navigate('/business-expert/financial')}
              >
                <DollarSign className="h-6 w-6" />
                <span>گزارش‌های مالی</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-auto p-4 flex flex-col items-center space-y-2"
                onClick={() => navigate('/business-expert/communication')}
              >
                <Activity className="h-6 w-6" />
                <span>ارتباط با مشتریان</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </BusinessExpertLayout>
  );
}
