import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Search, Plus, Upload, Edit, Trash2, MapPin, Phone, Building, ArrowLeft } from 'lucide-react';

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
      const response = await fetch('/api/business-expert/providers');
      if (response.ok) {
        const data = await response.json();
        setProviders(data.providers || []);
      } else {
        throw new Error('خطا در دریافت اطلاعات');
      }
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
      const response = await fetch(`/api/business-expert/providers/${providerId}/toggle-status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (response.ok) {
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
      } else {
        throw new Error('خطا در تغییر وضعیت');
      }
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
      const response = await fetch(`/api/business-expert/providers/${providerId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setProviders(prev => prev.filter(provider => provider.id !== providerId));
        toast({
          title: 'ارائه‌دهنده حذف شد',
          description: 'ارائه‌دهنده با موفقیت حذف شد.',
        });
      } else {
        throw new Error('خطا در حذف ارائه‌دهنده');
      }
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
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>در حال بارگذاری...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={() => navigate('/business-expert/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            بازگشت به داشبورد
          </Button>
          
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                مدیریت ارائه‌دهندگان
              </h1>
              <p className="text-muted-foreground">
                مدیریت و ویرایش اطلاعات ارائه‌دهندگان خدمات
              </p>
            </div>
            
            <div className="flex gap-2">
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
        </div>

        {/* فیلترها */}
        <Card className="mb-6">
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
                            >
                              {provider.is_active ? 'غیرفعال' : 'فعال'}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => navigate(`/business-expert/providers/${provider.id}/edit`)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDeleteProvider(provider.id)}
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
    </div>
  );
};
