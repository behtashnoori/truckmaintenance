import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { PageNavigation } from '@/components/PageNavigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';
import BusinessExpertLayout from '@/components/business-expert/BusinessExpertLayout';
import { Search, Plus, Upload, Trash2, MapPin, Phone, Building } from 'lucide-react';

interface Provider {
  id: number;
  name: string;
  address: string;
  phone_mobile: string;
  phone_landline?: string;
  latitude: number;
  longitude: number;
  is_active: boolean;
  categories: Array<{
    id: number;
    name: string;
  }>;
}

export const ManageProviders: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [providers, setProviders] = useState<Provider[]>([]);
  const [filteredProviders, setFilteredProviders] = useState<Provider[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');

  useEffect(() => {
    fetchProviders();
  }, []);

  useEffect(() => {
    filterProviders();
  }, [providers, searchTerm, statusFilter, categoryFilter]);

  const fetchProviders = async () => {
    try {
      setIsLoading(true);
      const response = await apiFetch('/api/business-expert/providers');
      setProviders(response.items || []);
    } catch (error) {
      console.error('Error fetching providers:', error);
      toast({
        title: 'خطا',
        description: 'خطا در دریافت اطلاعات ارائه‌دهندگان.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const filterProviders = () => {
    let filtered = providers;

    // جستجو
    if (searchTerm) {
      filtered = filtered.filter(provider =>
        provider.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        provider.phone_mobile.includes(searchTerm) ||
        provider.address.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // فیلتر وضعیت
    if (statusFilter !== 'all') {
      filtered = filtered.filter(provider =>
        statusFilter === 'active' ? provider.is_active : !provider.is_active
      );
    }

    // فیلتر دسته‌بندی
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(provider =>
        provider.categories.some(cat => cat.name === categoryFilter)
      );
    }

    setFilteredProviders(filtered);
  };

  const handleToggleStatus = async (providerId: number, currentStatus: boolean) => {
    try {
      await apiFetch(`/api/business-expert/providers/${providerId}/toggle-status`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      setProviders(prev =>
        prev.map(provider =>
          provider.id === providerId
            ? { ...provider, is_active: !currentStatus }
            : provider
        )
      );
      toast({
        title: 'وضعیت تغییر کرد',
        description: `ارائه‌دهنده ${!currentStatus ? 'فعال' : 'غیرفعال'} شد.`,
      });
    } catch (error) {
      console.error('Error toggling status:', error);
      toast({
        title: 'خطا',
        description: 'خطا در تغییر وضعیت ارائه‌دهنده.',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteProvider = async (providerId: number) => {
    if (!confirm('آیا از حذف این ارائه‌دهنده اطمینان دارید؟')) return;

    try {
      await apiFetch(`/api/business-expert/providers/${providerId}`, {
        method: 'DELETE',
      });

      setProviders(prev => prev.filter(provider => provider.id !== providerId));
      toast({
        title: 'ارائه‌دهنده حذف شد',
        description: 'ارائه‌دهنده با موفقیت حذف شد.',
      });
    } catch (error) {
      console.error('Error deleting provider:', error);
      toast({
        title: 'خطا',
        description: 'خطا در حذف ارائه‌دهنده.',
        variant: 'destructive',
      });
    }
  };

  const getUniqueCategories = () => {
    const categories = new Set<string>();
    providers.forEach(provider => {
      provider.categories.forEach(cat => categories.add(cat.name));
    });
    return Array.from(categories);
  };

  if (isLoading) {
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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              مدیریت ارائه‌دهندگان
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              مدیریت و ویرایش اطلاعات ارائه‌دهندگان خدمات
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex gap-2">
            <Button
              onClick={() => navigate('/business-expert/providers/add')}
              className="bg-green-600 hover:bg-green-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              اضافه کردن
            </Button>
            <Button
              onClick={() => navigate('/business-expert/providers/bulk-upload')}
              variant="outline"
            >
              <Upload className="w-4 h-4 mr-2" />
              آپلود انبوه
            </Button>
          </div>
        </div>

        {/* فیلترها */}
        <Card>
          <CardHeader>
            <CardTitle>فیلترها و جستجو</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <Input
                  placeholder="جستجو در نام، شماره تلفن یا آدرس..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="وضعیت" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه</SelectItem>
                  <SelectItem value="active">فعال</SelectItem>
                  <SelectItem value="inactive">غیرفعال</SelectItem>
                </SelectContent>
              </Select>

              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="دسته‌بندی" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه دسته‌ها</SelectItem>
                  {getUniqueCategories().map(category => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <div className="text-sm text-muted-foreground flex items-center">
                {filteredProviders.length} از {providers.length} ارائه‌دهنده
              </div>
            </div>
          </CardContent>
        </Card>

        {/* جدول ارائه‌دهندگان */}
        <Card>
          <CardHeader>
            <CardTitle>لیست ارائه‌دهندگان</CardTitle>
          </CardHeader>
          <CardContent>
            {filteredProviders.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Building className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>هیچ ارائه‌دهنده‌ای یافت نشد</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>نام مجموعه</TableHead>
                      <TableHead>آدرس</TableHead>
                      <TableHead>تلفن</TableHead>
                      <TableHead>دسته‌بندی</TableHead>
                      <TableHead>وضعیت</TableHead>
                      <TableHead>عملیات</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredProviders.map((provider) => (
                      <TableRow key={provider.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <Building className="w-4 h-4" />
                            {provider.name}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            <span className="max-w-xs truncate">
                              {provider.address}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Phone className="w-4 h-4" />
                            <div>
                              <div className="font-mono text-sm">
                                {provider.phone_mobile}
                              </div>
                              {provider.phone_landline && (
                                <div className="font-mono text-xs text-muted-foreground">
                                  {provider.phone_landline}
                                </div>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {provider.categories.map((category) => (
                              <Badge key={category.id} variant="secondary">
                                {category.name}
                              </Badge>
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={provider.is_active ? 'default' : 'destructive'}
                          >
                            {provider.is_active ? 'فعال' : 'غیرفعال'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleToggleStatus(provider.id, provider.is_active)}
                              title={provider.is_active ? 'غیرفعال کردن' : 'فعال کردن'}
                            >
                              {provider.is_active ? 'غیرفعال' : 'فعال'}
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDeleteProvider(provider.id)}
                              title="حذف ارائه‌دهنده"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </BusinessExpertLayout>
  );
};
