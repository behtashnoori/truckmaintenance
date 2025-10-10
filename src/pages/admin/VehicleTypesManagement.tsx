import React, { useState, useEffect } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Truck,
  Search,
  Save,
  X
} from 'lucide-react';

interface VehicleType {
  id: number;
  name: string;
  name_en: string;
  description: string | null;
  icon: string | null;
  capacity_min: number | null;
  capacity_max: number | null;
  is_active: boolean;
  created_at?: string;
}

export const VehicleTypesManagement: React.FC = () => {
  const { toast } = useToast();

  const [vehicleTypes, setVehicleTypes] = useState<VehicleType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingType, setEditingType] = useState<VehicleType | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    name_en: '',
    description: '',
    icon: '',
    capacity_min: '',
    capacity_max: '',
    is_active: true
  });

  useEffect(() => {
    fetchVehicleTypes();
  }, []);

  const fetchVehicleTypes = async () => {
    try {
      setIsLoading(true);
      const response = await apiFetch<any>('/api/admin/vehicle-types?per_page=100&include_inactive=true');
      setVehicleTypes(response.data || []);
    } catch (error) {
      toast({
        title: "خطا",
        description: "دریافت لیست انواع وسایل نقلیه با خطا مواجه شد",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const dataToSend = {
        name: formData.name,
        name_en: formData.name_en,
        description: formData.description || null,
        icon: formData.icon || null,
        capacity_min: formData.capacity_min ? parseInt(formData.capacity_min) : null,
        capacity_max: formData.capacity_max ? parseInt(formData.capacity_max) : null,
        is_active: formData.is_active
      };

      if (editingType) {
        await apiFetch(`/api/admin/vehicle-types/${editingType.id}`, {
          method: 'PUT',
          body: JSON.stringify(dataToSend),
        });
        toast({
          title: "موفقیت",
          description: "نوع وسیله نقلیه با موفقیت بروزرسانی شد",
        });
      } else {
        await apiFetch('/api/admin/vehicle-types', {
          method: 'POST',
          body: JSON.stringify(dataToSend),
        });
        toast({
          title: "موفقیت",
          description: "نوع وسیله نقلیه با موفقیت ایجاد شد",
        });
      }

      setIsDialogOpen(false);
      resetForm();
      fetchVehicleTypes();
    } catch (error: any) {
      toast({
        title: "خطا",
        description: error.message || "عملیات با خطا مواجه شد",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (vehicleType: VehicleType) => {
    setEditingType(vehicleType);
    setFormData({
      name: vehicleType.name,
      name_en: vehicleType.name_en,
      description: vehicleType.description || '',
      icon: vehicleType.icon || '',
      capacity_min: vehicleType.capacity_min?.toString() || '',
      capacity_max: vehicleType.capacity_max?.toString() || '',
      is_active: vehicleType.is_active
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('آیا از حذف این نوع وسیله نقلیه اطمینان دارید؟')) return;
    
    try {
      await apiFetch(`/api/admin/vehicle-types/${id}`, {
        method: 'DELETE',
      });
      toast({
        title: "موفقیت",
        description: "نوع وسیله نقلیه با موفقیت حذف شد",
      });
      fetchVehicleTypes();
    } catch (error: any) {
      toast({
        title: "خطا",
        description: error.message || "حذف با خطا مواجه شد",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      name_en: '',
      description: '',
      icon: '',
      capacity_min: '',
      capacity_max: '',
      is_active: true
    });
    setEditingType(null);
  };

  const filteredTypes = vehicleTypes.filter(vt => 
    vt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vt.name_en.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">مدیریت انواع وسایل نقلیه</h1>
            <p className="text-muted-foreground mt-1">
              تعریف و مدیریت انواع وسایل نقلیه سنگین
            </p>
          </div>
          
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="ml-2 h-4 w-4" />
                افزودن نوع جدید
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>
                  {editingType ? 'ویرایش نوع وسیله نقلیه' : 'افزودن نوع جدید'}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">نام فارسی</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="مثال: کامیون"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="name_en">نام انگلیسی</Label>
                  <Input
                    id="name_en"
                    value={formData.name_en}
                    onChange={(e) => setFormData({...formData, name_en: e.target.value})}
                    placeholder="مثال: truck"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">توضیحات</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    placeholder="توضیحات مختصر درباره این نوع وسیله..."
                    rows={3}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="icon">نام آیکون</Label>
                  <Input
                    id="icon"
                    value={formData.icon}
                    onChange={(e) => setFormData({...formData, icon: e.target.value})}
                    placeholder="مثال: Truck"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="capacity_min">حداقل ظرفیت (تن)</Label>
                    <Input
                      id="capacity_min"
                      type="number"
                      value={formData.capacity_min}
                      onChange={(e) => setFormData({...formData, capacity_min: e.target.value})}
                      placeholder="2"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="capacity_max">حداکثر ظرفیت (تن)</Label>
                    <Input
                      id="capacity_max"
                      type="number"
                      value={formData.capacity_max}
                      onChange={(e) => setFormData({...formData, capacity_max: e.target.value})}
                      placeholder="20"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-4 pt-4 border-t">
                  <Button type="submit" className="flex-1">
                    <Save className="ml-2 h-4 w-4" />
                    {editingType ? 'بروزرسانی' : 'ایجاد'}
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => setIsDialogOpen(false)}
                    className="flex-1"
                  >
                    <X className="ml-2 h-4 w-4" />
                    انصراف
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Truck className="h-5 w-5" />
                لیست انواع وسایل نقلیه
              </CardTitle>
              <div className="relative">
                <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="جستجو..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pr-9 w-64"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">در حال بارگذاری...</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>نام فارسی</TableHead>
                    <TableHead>نام انگلیسی</TableHead>
                    <TableHead>ظرفیت (تن)</TableHead>
                    <TableHead>توضیحات</TableHead>
                    <TableHead>وضعیت</TableHead>
                    <TableHead className="text-left">عملیات</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTypes.map((vt) => (
                    <TableRow key={vt.id}>
                      <TableCell className="font-medium">{vt.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{vt.name_en}</Badge>
                      </TableCell>
                      <TableCell className="text-sm">
                        {vt.capacity_min && vt.capacity_max 
                          ? `${vt.capacity_min} - ${vt.capacity_max}`
                          : '-'
                        }
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground max-w-md truncate">
                        {vt.description || '-'}
                      </TableCell>
                      <TableCell>
                        <Badge variant={vt.is_active ? "default" : "secondary"}>
                          {vt.is_active ? 'فعال' : 'غیرفعال'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 justify-end">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(vt)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(vt.id)}
                            className="text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            
            {!isLoading && filteredTypes.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                هیچ نوع وسیله نقلیه‌ای یافت نشد
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

