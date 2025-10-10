import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PageNavigation } from '@/components/PageNavigation';
import AdminLayout from '@/components/admin/AdminLayout';
import { Search, Filter, Eye, Check, X, Clock } from 'lucide-react';
import { apiFetch } from '@/utils/api';

interface Application {
  id: number;
  company_name: string;
  contact_person: string;
  phone: string;
  email: string;
  service_category: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  reviewed_at?: string;
  reviewer_name?: string;
}

export default function ApplicationsManagement() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const navigate = useNavigate();

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/admin/applications');
      setApplications(response.applications || []);
    } catch (err) {
      console.error('Error loading applications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await apiFetch(`/api/admin/applications/${id}/approve`, {
        method: 'POST'
      });
      await loadApplications();
    } catch (err) {
      console.error('Error approving application:', err);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await apiFetch(`/api/admin/applications/${id}/reject`, {
        method: 'POST'
      });
      await loadApplications();
    } catch (err) {
      console.error('Error rejecting application:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge variant="default" className="bg-green-500">تأیید شده</Badge>;
      case 'rejected':
        return <Badge variant="destructive">رد شده</Badge>;
      case 'pending':
        return <Badge variant="secondary">در انتظار بررسی</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.contact_person.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || app.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || app.service_category === categoryFilter;
    
    return matchesSearch && matchesStatus && matchesCategory;
  });

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
            <h1 className="text-3xl font-bold">مدیریت درخواست‌ها</h1>
            <p className="text-muted-foreground">
              بررسی و مدیریت درخواست‌های ثبت‌نام ارائه‌دهندگان خدمات
            </p>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کل درخواست‌ها</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{applications.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">در انتظار بررسی</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {applications.filter(app => app.status === 'pending').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">تأیید شده</CardTitle>
              <Check className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {applications.filter(app => app.status === 'approved').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">رد شده</CardTitle>
              <X className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {applications.filter(app => app.status === 'rejected').length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>فیلتر و جستجو</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="جستجو در نام شرکت، تماس گیرنده یا ایمیل..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="وضعیت" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه وضعیت‌ها</SelectItem>
                  <SelectItem value="pending">در انتظار بررسی</SelectItem>
                  <SelectItem value="approved">تأیید شده</SelectItem>
                  <SelectItem value="rejected">رد شده</SelectItem>
                </SelectContent>
              </Select>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="دسته‌بندی" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه دسته‌بندی‌ها</SelectItem>
                  <SelectItem value="maintenance">تعمیر و نگهداری</SelectItem>
                  <SelectItem value="towing">کشیدن و یدک</SelectItem>
                  <SelectItem value="fuel">سوخت</SelectItem>
                  <SelectItem value="parts">قطعات</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Applications List */}
        <div className="space-y-4">
          {filteredApplications.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-muted-foreground">
                  {applications.length === 0 
                    ? "هنوز هیچ درخواستی ثبت نشده است"
                    : "هیچ درخواستی با این فیلترها یافت نشد"
                  }
                </div>
              </CardContent>
            </Card>
          ) : (
            filteredApplications.map((app) => (
              <Card key={app.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold">{app.company_name}</h3>
                        {getStatusBadge(app.status)}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground">
                        <div>
                          <strong>تماس گیرنده:</strong> {app.contact_person}
                        </div>
                        <div>
                          <strong>تلفن:</strong> {app.phone}
                        </div>
                        <div>
                          <strong>ایمیل:</strong> {app.email}
                        </div>
                        <div>
                          <strong>دسته‌بندی:</strong> {app.service_category}
                        </div>
                        <div className="md:col-span-2">
                          <strong>توضیحات:</strong> {app.description}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ثبت شده در: {new Date(app.created_at).toLocaleDateString('fa-IR')}
                        {app.reviewed_at && (
                          <span className="mr-4">
                            بررسی شده در: {new Date(app.reviewed_at).toLocaleDateString('fa-IR')}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/admin/applications/${app.id}`)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        مشاهده جزئیات
                      </Button>
                      {app.status === 'pending' && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleApprove(app.id)}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            <Check className="h-4 w-4 mr-2" />
                            تأیید
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleReject(app.id)}
                          >
                            <X className="h-4 w-4 mr-2" />
                            رد
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        <PageNavigation />
      </div>
    </AdminLayout>
  );
}
