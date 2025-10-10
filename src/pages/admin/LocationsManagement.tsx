import React, { useState, useEffect } from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';
import { 
  Plus, 
  Edit, 
  Trash2, 
  MapPin,
  Search,
  Save,
  X
} from 'lucide-react';

interface Location {
  id: number;
  name: string;
  type: 'province' | 'county' | 'city';
  lat: number;
  lon: number;
  parent_id: number | null;
  is_active: boolean;
  created_at?: string;
  children?: Location[];
}

export const LocationsManagement: React.FC = () => {
  const { toast } = useToast();

  const [locations, setLocations] = useState<Location[]>([]);
  const [provinces, setProvinces] = useState<Location[]>([]);
  const [counties, setCounties] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  
  const [formData, setFormData] = useState({
    name: '',
    type: 'province' as 'province' | 'county' | 'city',
    lat: '',
    lon: '',
    parent_id: null as number | null,
    is_active: true
  });

  useEffect(() => {
    fetchLocations();
    fetchProvinces();
  }, []);

  const fetchLocations = async () => {
    try {
      setIsLoading(true);
      const response = await apiFetch<any>('/api/admin/locations?per_page=500&include_inactive=true');
      setLocations(response.data || []);
    } catch (error) {
      toast({
        title: "خطا",
        description: "دریافت لیست مکان‌ها با خطا مواجه شد",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProvinces = async () => {
    try {
      const response = await apiFetch<any>('/api/admin/locations?type=province&per_page=100');
      setProvinces(response.data || []);
    } catch (error) {
      console.error('Error fetching provinces:', error);
    }
  };

  const fetchCounties = async (provinceId: number) => {
    try {
      const response = await apiFetch<any>(`/api/admin/locations?type=county&parent_id=${provinceId}&per_page=100`);
      setCounties(response.data || []);
    } catch (error) {
      console.error('Error fetching counties:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const dataToSend = {
        ...formData,
        latitude: parseFloat(formData.lat),
        longitude: parseFloat(formData.lon),
      };

      if (editingLocation) {
        await apiFetch(`/api/admin/locations/${editingLocation.id}`, {
          method: 'PUT',
          body: JSON.stringify(dataToSend),
        });
        toast({
          title: "موفقیت",
          description: "مکان با موفقیت بروزرسانی شد",
        });
      } else {
        await apiFetch('/api/admin/locations', {
          method: 'POST',
          body: JSON.stringify(dataToSend),
        });
        toast({
          title: "موفقیت",
          description: "مکان با موفقیت ایجاد شد",
        });
      }

      setIsDialogOpen(false);
      resetForm();
      fetchLocations();
    } catch (error: any) {
      toast({
        title: "خطا",
        description: error.message || "عملیات با خطا مواجه شد",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (location: Location) => {
    setEditingLocation(location);
    setFormData({
      name: location.name,
      type: location.type,
      lat: location.lat.toString(),
      lon: location.lon.toString(),
      parent_id: location.parent_id,
      is_active: location.is_active
    });
    
    if (location.type === 'city' && location.parent_id) {
      const county = locations.find(l => l.id === location.parent_id);
      if (county && county.parent_id) {
        fetchCounties(county.parent_id);
      }
    }
    
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('آیا از حذف این مکان اطمینان دارید؟')) return;
    
    try {
      await apiFetch(`/api/admin/locations/${id}`, {
        method: 'DELETE',
      });
      toast({
        title: "موفقیت",
        description: "مکان با موفقیت حذف شد",
      });
      fetchLocations();
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
      type: 'province',
      lat: '',
      lon: '',
      parent_id: null,
      is_active: true
    });
    setEditingLocation(null);
    setCounties([]);
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'province': return 'استان';
      case 'county': return 'شهرستان';
      case 'city': return 'شهر';
      default: return type;
    }
  };

  const getParentName = (parentId: number | null) => {
    if (!parentId) return '-';
    const parent = locations.find(l => l.id === parentId);
    return parent ? parent.name : '-';
  };

  const filteredLocations = locations.filter(location => {
    const matchesSearch = location.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || location.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">مدیریت مکان‌ها</h1>
            <p className="text-muted-foreground mt-1">
              مدیریت استان‌ها، شهرستان‌ها و شهرها
            </p>
          </div>
          
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="ml-2 h-4 w-4" />
                افزودن مکان جدید
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>
                  {editingLocation ? 'ویرایش مکان' : 'افزودن مکان جدید'}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">نام مکان</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="مثال: تهران"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="type">نوع مکان</Label>
                  <Select
                    value={formData.type}
                    onValueChange={(value: any) => {
                      setFormData({...formData, type: value, parent_id: null});
                      setCounties([]);
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="نوع را انتخاب کنید" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="province">استان</SelectItem>
                      <SelectItem value="county">شهرستان</SelectItem>
                      <SelectItem value="city">شهر</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {formData.type === 'county' && (
                  <div className="space-y-2">
                    <Label htmlFor="province">استان</Label>
                    <Select
                      value={formData.parent_id?.toString() || ''}
                      onValueChange={(value) => setFormData({...formData, parent_id: parseInt(value)})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="استان را انتخاب کنید" />
                      </SelectTrigger>
                      <SelectContent>
                        {provinces.map((province) => (
                          <SelectItem key={province.id} value={province.id.toString()}>
                            {province.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {formData.type === 'city' && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="province">استان</Label>
                      <Select
                        value={formData.parent_id?.toString() || ''}
                        onValueChange={(value) => {
                          const provinceId = parseInt(value);
                          fetchCounties(provinceId);
                          setFormData({...formData, parent_id: null});
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="استان را انتخاب کنید" />
                        </SelectTrigger>
                        <SelectContent>
                          {provinces.map((province) => (
                            <SelectItem key={province.id} value={province.id.toString()}>
                              {province.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {counties.length > 0 && (
                      <div className="space-y-2">
                        <Label htmlFor="county">شهرستان</Label>
                        <Select
                          value={formData.parent_id?.toString() || ''}
                          onValueChange={(value) => setFormData({...formData, parent_id: parseInt(value)})}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="شهرستان را انتخاب کنید" />
                          </SelectTrigger>
                          <SelectContent>
                            {counties.map((county) => (
                              <SelectItem key={county.id} value={county.id.toString()}>
                                {county.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </>
                )}

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="lat">عرض جغرافیایی</Label>
                    <Input
                      id="lat"
                      type="number"
                      step="0.0001"
                      value={formData.lat}
                      onChange={(e) => setFormData({...formData, lat: e.target.value})}
                      placeholder="35.6892"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lon">طول جغرافیایی</Label>
                    <Input
                      id="lon"
                      type="number"
                      step="0.0001"
                      value={formData.lon}
                      onChange={(e) => setFormData({...formData, lon: e.target.value})}
                      placeholder="51.3890"
                      required
                    />
                  </div>
                </div>

                <div className="flex items-center gap-4 pt-4 border-t">
                  <Button type="submit" className="flex-1">
                    <Save className="ml-2 h-4 w-4" />
                    {editingLocation ? 'بروزرسانی' : 'ایجاد'}
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
                <MapPin className="h-5 w-5" />
                لیست مکان‌ها
              </CardTitle>
              <div className="flex items-center gap-2">
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="نوع مکان" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">همه</SelectItem>
                    <SelectItem value="province">استان</SelectItem>
                    <SelectItem value="county">شهرستان</SelectItem>
                    <SelectItem value="city">شهر</SelectItem>
                  </SelectContent>
                </Select>
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
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">در حال بارگذاری...</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>نام</TableHead>
                    <TableHead>نوع</TableHead>
                    <TableHead>والد</TableHead>
                    <TableHead>مختصات</TableHead>
                    <TableHead>وضعیت</TableHead>
                    <TableHead className="text-left">عملیات</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLocations.map((location) => (
                    <TableRow key={location.id}>
                      <TableCell className="font-medium">{location.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {getTypeLabel(location.type)}
                        </Badge>
                      </TableCell>
                      <TableCell>{getParentName(location.parent_id)}</TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
                      </TableCell>
                      <TableCell>
                        <Badge variant={location.is_active ? "default" : "secondary"}>
                          {location.is_active ? 'فعال' : 'غیرفعال'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 justify-end">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleEdit(location)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(location.id)}
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
            
            {!isLoading && filteredLocations.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                هیچ مکانی یافت نشد
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AdminLayout>
  );
};

