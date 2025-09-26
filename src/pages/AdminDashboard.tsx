import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiFetch } from '@/utils/api';
import AdminLayout from '@/components/admin/AdminLayout';
import { Tag, Plus, Settings } from 'lucide-react';

interface DashboardStats {
  total_applications: number;
  pending_applications: number;
  approved_applications: number;
  active_support: number;
}

interface Application {
  id: number;
  company_name: string;
  representative_first_name: string;
  representative_last_name: string;
  phone_mobile: string;
  service_domain: string;
  status: string;
  created_at: string;
  is_approved: boolean;
  reviewer_name?: string;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsResponse, applicationsResponse] = await Promise.all([
        apiFetch('/dashboard'),
        apiFetch('/applications')
      ]);
      
      setStats(statsResponse);
      setApplications(applicationsResponse.applications);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await apiFetch('/logout', { method: 'POST' });
      navigate('/admin/login');
    } catch (err) {
      console.error('Error logging out:', err);
    }
  };

  const getStatusBadge = (status: string, isApproved: boolean) => {
    if (isApproved) {
      return <Badge variant="default" className="bg-green-500">تأیید شده</Badge>;
    } else if (status === 'pending') {
      return <Badge variant="secondary">در انتظار بررسی</Badge>;
    } else {
      return <Badge variant="destructive">رد شده</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">در حال بارگذاری...</div>
      </div>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">داشبورد ادمین</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              نمای کلی سیستم و آمار درخواست‌ها
            </p>
          </div>
        </div>

        <div>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کل درخواست‌ها</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.total_applications || 0}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">در انتظار بررسی</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats?.pending_applications || 0}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">تأیید شده</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats?.approved_applications || 0}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کارشناسان فعال</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.active_support || 0}</div>
            </CardContent>
          </Card>
        </div>

        {/* Category Management Quick Actions */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Tag className="h-5 w-5" />
              مدیریت دسته‌بندی‌ها
            </CardTitle>
            <CardDescription>
              تعریف و مدیریت دسته‌بندی‌های حوزه ارائه‌دهندگان خدمات
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button
                onClick={() => navigate('/admin/categories')}
                className="h-20 flex flex-col items-center justify-center gap-2"
                variant="outline"
              >
                <Tag className="h-6 w-6" />
                <span>مدیریت دسته‌بندی‌ها</span>
              </Button>
              
              <Button
                onClick={() => navigate('/admin/categories')}
                className="h-20 flex flex-col items-center justify-center gap-2"
                variant="outline"
              >
                <Plus className="h-6 w-6" />
                <span>اضافه کردن دسته‌بندی جدید</span>
              </Button>
            </div>
          </CardContent>
        </Card>

          {/* Applications Table */}
          <Card>
            <CardHeader>
              <CardTitle>درخواست‌های ارائه‌دهندگان</CardTitle>
              <CardDescription>
                لیست تمام درخواست‌های ثبت شده توسط ارائه‌دهندگان خدمات
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-right py-3 px-4">شرکت</th>
                      <th className="text-right py-3 px-4">نماینده</th>
                      <th className="text-right py-3 px-4">تلفن</th>
                      <th className="text-right py-3 px-4">حوزه خدمات</th>
                      <th className="text-right py-3 px-4">وضعیت</th>
                      <th className="text-right py-3 px-4">تاریخ ثبت</th>
                      <th className="text-right py-3 px-4">عملیات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {applications.map((app) => (
                      <tr key={app.id} className="border-b">
                        <td className="py-3 px-4">{app.company_name}</td>
                        <td className="py-3 px-4">
                          {app.representative_first_name} {app.representative_last_name}
                        </td>
                        <td className="py-3 px-4">{app.phone_mobile}</td>
                        <td className="py-3 px-4">{app.service_domain}</td>
                        <td className="py-3 px-4">{getStatusBadge(app.status, app.is_approved)}</td>
                        <td className="py-3 px-4">
                          {new Date(app.created_at).toLocaleDateString('fa-IR')}
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              onClick={() => navigate(`/admin/applications/${app.id}`)}
                            >
                              مشاهده
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AdminLayout>
  );
}

