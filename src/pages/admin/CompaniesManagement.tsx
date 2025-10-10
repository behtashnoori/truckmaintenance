import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PageNavigation } from '@/components/PageNavigation';
import AdminLayout from '@/components/admin/AdminLayout';
import { Search, Building, Eye, Edit, Trash2, Plus, Users } from 'lucide-react';
import { apiFetch } from '@/utils/api';

interface Company {
  id: number;
  name: string;
  registration_number: string;
  contact_person: string;
  phone: string;
  email: string;
  address: string;
  service_categories: string[];
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  total_providers: number;
  total_applications: number;
}

export default function CompaniesManagement() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const navigate = useNavigate();

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/admin/companies');
      setCompanies(response.companies || []);
    } catch (err) {
      console.error('Error loading companies:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (id: number, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
      await apiFetch(`/api/admin/companies/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus })
      });
      await loadCompanies();
    } catch (err) {
      console.error('Error updating company status:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('آیا از حذف این شرکت اطمینان دارید؟')) return;
    
    try {
      await apiFetch(`/api/admin/companies/${id}`, {
        method: 'DELETE'
      });
      await loadCompanies();
    } catch (err) {
      console.error('Error deleting company:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-green-500">فعال</Badge>;
      case 'inactive':
        return <Badge variant="secondary">غیرفعال</Badge>;
      case 'suspended':
        return <Badge variant="destructive">معلق</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const filteredCompanies = companies.filter(company => {
    const matchesSearch = company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         company.registration_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         company.contact_person.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         company.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || company.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || 
                           company.service_categories.some(cat => cat === categoryFilter);
    
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
            <h1 className="text-3xl font-bold">مدیریت شرکت‌ها</h1>
            <p className="text-muted-foreground">
              مدیریت اطلاعات شرکت‌های ثبت‌نام شده و ارائه‌دهندگان خدمات
            </p>
          </div>
          <Button onClick={() => navigate('/admin/companies/add')}>
            <Plus className="h-4 w-4 mr-2" />
            افزودن شرکت جدید
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کل شرکت‌ها</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{companies.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">شرکت‌های فعال</CardTitle>
              <Building className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {companies.filter(company => company.status === 'active').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کل ارائه‌دهندگان</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {companies.reduce((sum, company) => sum + company.total_providers, 0)}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کل درخواست‌ها</CardTitle>
              <Users className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {companies.reduce((sum, company) => sum + company.total_applications, 0)}
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
                  placeholder="جستجو در نام شرکت، شماره ثبت، تماس گیرنده یا ایمیل..."
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
                  <SelectItem value="active">فعال</SelectItem>
                  <SelectItem value="inactive">غیرفعال</SelectItem>
                  <SelectItem value="suspended">معلق</SelectItem>
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

        {/* Companies List */}
        <div className="space-y-4">
          {filteredCompanies.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-muted-foreground">
                  {companies.length === 0 
                    ? "هنوز هیچ شرکتی ثبت نشده است"
                    : "هیچ شرکتی با این فیلترها یافت نشد"
                  }
                </div>
              </CardContent>
            </Card>
          ) : (
            filteredCompanies.map((company) => (
              <Card key={company.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold">{company.name}</h3>
                        {getStatusBadge(company.status)}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground">
                        <div>
                          <strong>شماره ثبت:</strong> {company.registration_number}
                        </div>
                        <div>
                          <strong>تماس گیرنده:</strong> {company.contact_person}
                        </div>
                        <div>
                          <strong>تلفن:</strong> {company.phone}
                        </div>
                        <div>
                          <strong>ایمیل:</strong> {company.email}
                        </div>
                        <div className="md:col-span-2">
                          <strong>آدرس:</strong> {company.address}
                        </div>
                        <div className="md:col-span-2">
                          <strong>دسته‌بندی‌های خدمات:</strong> 
                          <div className="flex flex-wrap gap-1 mt-1">
                            {company.service_categories.map((category, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {category}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-4 text-xs text-muted-foreground">
                        <span>ارائه‌دهندگان: {company.total_providers}</span>
                        <span>درخواست‌ها: {company.total_applications}</span>
                        <span>ثبت شده در: {new Date(company.created_at).toLocaleDateString('fa-IR')}</span>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/admin/companies/${company.id}`)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        مشاهده
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/admin/companies/${company.id}/edit`)}
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        ویرایش
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleStatus(company.id, company.status)}
                        className={company.status === 'active' ? 'text-orange-600 hover:text-orange-700' : 'text-green-600 hover:text-green-700'}
                      >
                        {company.status === 'active' ? 'غیرفعال کردن' : 'فعال کردن'}
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(company.id)}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        حذف
                      </Button>
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
