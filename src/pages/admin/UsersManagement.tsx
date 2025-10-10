import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { PageNavigation } from '@/components/PageNavigation';
import AdminLayout from '@/components/admin/AdminLayout';
import { Search, Users, UserPlus, Eye, Edit, Trash2, Shield, UserCheck, Save, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'business_expert' | 'support' | 'user';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export default function UsersManagement() {
  const { toast } = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    role: 'user' as 'admin' | 'business_expert' | 'support' | 'user',
    is_active: true
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/users');
      setUsers(response.users || response.data || []);
    } catch (err) {
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStatus = async (id: number, currentStatus: boolean) => {
    try {
      await apiFetch(`/api/users/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !currentStatus })
      });
      await loadUsers();
    } catch (err) {
      console.error('Error updating user status:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingUser) {
        await apiFetch(`/api/users/${editingUser.id}`, {
          method: 'PUT',
          body: JSON.stringify(formData),
        });
        toast({
          title: "موفقیت",
          description: "کاربر با موفقیت بروزرسانی شد",
        });
      } else {
        await apiFetch('/api/users', {
          method: 'POST',
          body: JSON.stringify(formData),
        });
        toast({
          title: "موفقیت",
          description: "کاربر با موفقیت ایجاد شد",
        });
      }

      setIsDialogOpen(false);
      resetForm();
      loadUsers();
    } catch (error: any) {
      toast({
        title: "خطا",
        description: error.message || "عملیات با خطا مواجه شد",
        variant: "destructive",
      });
    }
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      is_active: user.is_active
    });
    setIsDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      full_name: '',
      role: 'user',
      is_active: true
    });
    setEditingUser(null);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('آیا از حذف این کاربر اطمینان دارید؟')) return;
    
    try {
      await apiFetch(`/api/users/${id}`, {
        method: 'DELETE'
      });
      await loadUsers();
    } catch (err) {
      console.error('Error deleting user:', err);
    }
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'admin':
        return <Badge variant="default" className="bg-red-500">مدیر</Badge>;
      case 'business_expert':
        return <Badge variant="default" className="bg-blue-500">کارشناس کسب و کار</Badge>;
      case 'support':
        return <Badge variant="default" className="bg-green-500">پشتیبانی</Badge>;
      case 'user':
        return <Badge variant="secondary">کاربر</Badge>;
      default:
        return <Badge variant="outline">{role}</Badge>;
    }
  };

  const getStatusBadge = (isActive: boolean) => {
    return isActive ? 
      <Badge variant="default" className="bg-green-500">فعال</Badge> : 
      <Badge variant="secondary">غیرفعال</Badge>;
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.full_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'active' && user.is_active) ||
                         (statusFilter === 'inactive' && !user.is_active);
    
    return matchesSearch && matchesRole && matchesStatus;
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
            <h1 className="text-3xl font-bold">مدیریت کاربران</h1>
            <p className="text-muted-foreground">
              مدیریت کاربران سیستم و تعیین دسترسی‌ها و نقش‌ها
            </p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <UserPlus className="h-4 w-4 mr-2" />
                افزودن کاربر جدید
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]">
              <DialogHeader>
                <DialogTitle>
                  {editingUser ? 'ویرایش کاربر' : 'افزودن کاربر جدید'}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">نام کاربری</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    placeholder="نام کاربری"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">ایمیل</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="example@domain.com"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="full_name">نام کامل</Label>
                  <Input
                    id="full_name"
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    placeholder="نام و نام خانوادگی"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="role">نقش</Label>
                  <Select
                    value={formData.role}
                    onValueChange={(value: any) => setFormData({...formData, role: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="نقش را انتخاب کنید" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="user">کاربر عادی</SelectItem>
                      <SelectItem value="business_expert">کارشناس بازرگانی</SelectItem>
                      <SelectItem value="support">پشتیبانی</SelectItem>
                      <SelectItem value="admin">مدیر سیستم</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-4 pt-4 border-t">
                  <Button type="submit" className="flex-1">
                    <Save className="ml-2 h-4 w-4" />
                    {editingUser ? 'بروزرسانی' : 'ایجاد'}
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

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کل کاربران</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{users.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کاربران فعال</CardTitle>
              <UserCheck className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter(user => user.is_active).length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">مدیران</CardTitle>
              <Shield className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter(user => user.role === 'admin').length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">کارشناسان کسب و کار</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {users.filter(user => user.role === 'business_expert').length}
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
                  placeholder="جستجو در نام کاربری، ایمیل یا نام کامل..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={roleFilter} onValueChange={setRoleFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="نقش" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه نقش‌ها</SelectItem>
                  <SelectItem value="admin">مدیر</SelectItem>
                  <SelectItem value="business_expert">کارشناس کسب و کار</SelectItem>
                  <SelectItem value="support">پشتیبانی</SelectItem>
                  <SelectItem value="user">کاربر</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="وضعیت" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">همه وضعیت‌ها</SelectItem>
                  <SelectItem value="active">فعال</SelectItem>
                  <SelectItem value="inactive">غیرفعال</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Users List */}
        <div className="space-y-4">
          {filteredUsers.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-muted-foreground">
                  {users.length === 0 
                    ? "هنوز هیچ کاربری ثبت نشده است"
                    : "هیچ کاربری با این فیلترها یافت نشد"
                  }
                </div>
              </CardContent>
            </Card>
          ) : (
            filteredUsers.map((user) => (
              <Card key={user.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold">{user.full_name}</h3>
                        {getRoleBadge(user.role)}
                        {getStatusBadge(user.is_active)}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground">
                        <div>
                          <strong>نام کاربری:</strong> {user.username}
                        </div>
                        <div>
                          <strong>ایمیل:</strong> {user.email}
                        </div>
                        <div>
                          <strong>نقش:</strong> {user.role}
                        </div>
                        <div>
                          <strong>وضعیت:</strong> {user.is_active ? 'فعال' : 'غیرفعال'}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ثبت شده در: {new Date(user.created_at).toLocaleDateString('fa-IR')}
                        {user.last_login && (
                          <span className="mr-4">
                            آخرین ورود: {new Date(user.last_login).toLocaleDateString('fa-IR')}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/admin/users/${user.id}`)}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        مشاهده
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(user)}
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        ویرایش
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleStatus(user.id, user.is_active)}
                        className={user.is_active ? 'text-orange-600 hover:text-orange-700' : 'text-green-600 hover:text-green-700'}
                      >
                        {user.is_active ? 'غیرفعال کردن' : 'فعال کردن'}
                      </Button>
                      {user.role !== 'admin' && (
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(user.id)}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          حذف
                        </Button>
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
