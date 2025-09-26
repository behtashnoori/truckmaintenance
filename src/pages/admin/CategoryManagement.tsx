import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Tag, 
  Building, 
  ArrowLeft,
  Save,
  X,
  AlertTriangle
} from 'lucide-react';

interface Category {
  id: number;
  name: string;
  companies_count?: number;
  created_at?: string;
}

export const CategoryManagement: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [formData, setFormData] = useState({
    name: ''
  });

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/admin/categories');
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories || []);
      } else {
        throw new Error('خطا در دریافت دسته‌بندی‌ها');
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
      toast({
        title: 'خطا',
        description: 'خطا در دریافت دسته‌بندی‌ها.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      toast({
        title: 'خطا',
        description: 'نام دسته‌بندی الزامی است.',
        variant: 'destructive',
      });
      return;
    }

    try {
      const url = editingCategory 
        ? `/api/admin/categories/${editingCategory.id}`
        : '/api/admin/categories';
      
      const method = editingCategory ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (editingCategory) {
          setCategories(prev =>
            prev.map(cat => cat.id === editingCategory.id ? data.category : cat)
          );
          toast({
            title: 'دسته‌بندی به‌روزرسانی شد',
            description: 'دسته‌بندی با موفقیت به‌روزرسانی شد.',
          });
        } else {
          setCategories(prev => [...prev, data.category]);
          toast({
            title: 'دسته‌بندی اضافه شد',
            description: 'دسته‌بندی جدید با موفقیت اضافه شد.',
          });
        }
        
        setIsDialogOpen(false);
        setEditingCategory(null);
        setFormData({ name: '' });
      } else {
        const error = await response.json();
        throw new Error(error.message || 'خطا در ذخیره دسته‌بندی');
      }
    } catch (error) {
      console.error('Error saving category:', error);
      toast({
        title: 'خطا',
        description: 'خطا در ذخیره دسته‌بندی. لطفاً دوباره تلاش کنید.',
        variant: 'destructive',
      });
    }
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    setFormData({ name: category.name });
    setIsDialogOpen(true);
  };

  const handleDelete = async (categoryId: number) => {
    if (!confirm('آیا از حذف این دسته‌بندی اطمینان دارید؟ این عمل قابل بازگشت نیست.')) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/categories/${categoryId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setCategories(prev => prev.filter(cat => cat.id !== categoryId));
        toast({
          title: 'دسته‌بندی حذف شد',
          description: 'دسته‌بندی با موفقیت حذف شد.',
        });
      } else {
        const error = await response.json();
        throw new Error(error.message || 'خطا در حذف دسته‌بندی');
      }
    } catch (error) {
      console.error('Error deleting category:', error);
      toast({
        title: 'خطا',
        description: 'خطا در حذف دسته‌بندی. ممکن است این دسته‌بندی در حال استفاده باشد.',
        variant: 'destructive',
      });
    }
  };

  const handleCancel = () => {
    setIsDialogOpen(false);
    setEditingCategory(null);
    setFormData({ name: '' });
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
            onClick={() => navigate('/admin/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            بازگشت به داشبورد
          </Button>
          
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                مدیریت دسته‌بندی‌ها
              </h1>
              <p className="text-muted-foreground">
                تعریف و مدیریت دسته‌بندی‌های حوزه ارائه‌دهندگان خدمات
              </p>
            </div>
            
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => {
                  setEditingCategory(null);
                  setFormData({ name: '' });
                }}>
                  <Plus className="w-4 h-4 mr-2" />
                  اضافه کردن دسته‌بندی
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>
                    {editingCategory ? 'ویرایش دسته‌بندی' : 'اضافه کردن دسته‌بندی جدید'}
                  </DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="name">نام دسته‌بندی *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ name: e.target.value })}
                      placeholder="مثال: تعمیرات موتور"
                      required
                    />
                  </div>
                  
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={handleCancel}>
                      <X className="w-4 h-4 mr-2" />
                      انصراف
                    </Button>
                    <Button type="submit">
                      <Save className="w-4 h-4 mr-2" />
                      {editingCategory ? 'به‌روزرسانی' : 'ذخیره'}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* آمار کلی */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Tag className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">کل دسته‌بندی‌ها</p>
                  <p className="text-2xl font-bold">{categories.length}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Building className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">ارائه‌دهندگان فعال</p>
                  <p className="text-2xl font-bold">
                    {categories.reduce((sum, cat) => sum + (cat.companies_count || 0), 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <AlertTriangle className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-muted-foreground">دسته‌بندی‌های بدون ارائه‌دهنده</p>
                  <p className="text-2xl font-bold">
                    {categories.filter(cat => (cat.companies_count || 0) === 0).length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* جدول دسته‌بندی‌ها */}
        <Card>
          <CardHeader>
            <CardTitle>لیست دسته‌بندی‌ها</CardTitle>
          </CardHeader>
          <CardContent>
            {categories.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Tag className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>هیچ دسته‌بندی‌ای تعریف نشده است</p>
                <p className="text-sm">برای شروع، اولین دسته‌بندی را اضافه کنید</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>نام دسته‌بندی</TableHead>
                      <TableHead>تعداد ارائه‌دهندگان</TableHead>
                      <TableHead>وضعیت</TableHead>
                      <TableHead>عملیات</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {categories.map((category) => (
                      <TableRow key={category.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <Tag className="w-4 h-4" />
                            {category.name}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">
                            {category.companies_count || 0} ارائه‌دهنده
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={category.companies_count && category.companies_count > 0 ? 'default' : 'destructive'}
                          >
                            {category.companies_count && category.companies_count > 0 ? 'فعال' : 'بدون ارائه‌دهنده'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleEdit(category)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleDelete(category.id)}
                              disabled={category.companies_count && category.companies_count > 0}
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

        {/* راهنمای استفاده */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>راهنمای استفاده</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>نکات مهم:</strong>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>دسته‌بندی‌هایی که دارای ارائه‌دهنده هستند قابل حذف نیستند</li>
                    <li>تغییر نام دسته‌بندی بر روی تمام ارائه‌دهندگان آن دسته تأثیر می‌گذارد</li>
                    <li>دسته‌بندی‌های جدید بلافاصله در فرم‌های ثبت‌نام در دسترس قرار می‌گیرند</li>
                    <li>برای حذف یک دسته‌بندی، ابتدا تمام ارائه‌دهندگان آن را به دسته‌بندی دیگری منتقل کنید</li>
                  </ul>
                </AlertDescription>
              </Alert>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
