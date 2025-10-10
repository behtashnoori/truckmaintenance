import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { PageNavigation } from '@/components/PageNavigation';
import AdminLayout from '@/components/admin/AdminLayout';
import { Save, RefreshCw, Database, Mail, Shield, Globe, Bell } from 'lucide-react';
import { apiFetch } from '@/utils/api';
import { toast } from '@/hooks/use-toast';

interface SystemSettings {
  site_name: string;
  site_description: string;
  contact_email: string;
  admin_email: string;
  max_file_size: number;
  allowed_file_types: string[];
  email_notifications: boolean;
  sms_notifications: boolean;
  maintenance_mode: boolean;
  auto_approval: boolean;
  max_applications_per_day: number;
  session_timeout: number;
  password_policy: {
    min_length: number;
    require_special_chars: boolean;
    require_numbers: boolean;
    require_uppercase: boolean;
  };
  backup_settings: {
    auto_backup: boolean;
    backup_frequency: string;
    retention_days: number;
  };
}

export default function Settings() {
  const [settings, setSettings] = useState<SystemSettings>({
    site_name: '',
    site_description: '',
    contact_email: '',
    admin_email: '',
    max_file_size: 10,
    allowed_file_types: ['jpg', 'png', 'pdf', 'doc', 'docx'],
    email_notifications: true,
    sms_notifications: false,
    maintenance_mode: false,
    auto_approval: false,
    max_applications_per_day: 100,
    session_timeout: 60,
    password_policy: {
      min_length: 8,
      require_special_chars: true,
      require_numbers: true,
      require_uppercase: true,
    },
    backup_settings: {
      auto_backup: true,
      backup_frequency: 'daily',
      retention_days: 30,
    },
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/admin/settings');
      setSettings({ ...settings, ...response });
    } catch (err) {
      console.error('Error loading settings:', err);
      toast({
        title: "خطا",
        description: "خطا در بارگذاری تنظیمات",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await apiFetch('/api/admin/settings', {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      toast({
        title: "موفق",
        description: "تنظیمات با موفقیت ذخیره شد",
      });
    } catch (err) {
      console.error('Error saving settings:', err);
      toast({
        title: "خطا",
        description: "خطا در ذخیره تنظیمات",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (confirm('آیا از بازنشانی تنظیمات به حالت پیش‌فرض اطمینان دارید؟')) {
      loadSettings();
    }
  };

  const updateSetting = (key: string, value: any) => {
    if (key.includes('.')) {
      const [parent, child] = key.split('.');
      setSettings(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent as keyof SystemSettings],
          [child]: value
        }
      }));
    } else {
      setSettings(prev => ({
        ...prev,
        [key]: value
      }));
    }
  };

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
            <h1 className="text-3xl font-bold">تنظیمات سیستم</h1>
            <p className="text-muted-foreground">
              مدیریت تنظیمات کلی سیستم و پیکربندی
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset}>
              <RefreshCw className="h-4 w-4 mr-2" />
              بازنشانی
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'در حال ذخیره...' : 'ذخیره'}
            </Button>
          </div>
        </div>

        {/* General Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              تنظیمات عمومی
            </CardTitle>
            <CardDescription>
              تنظیمات اصلی سایت و اطلاعات تماس
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="site_name">نام سایت</Label>
                <Input
                  id="site_name"
                  value={settings.site_name}
                  onChange={(e) => updateSetting('site_name', e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="contact_email">ایمیل تماس</Label>
                <Input
                  id="contact_email"
                  type="email"
                  value={settings.contact_email}
                  onChange={(e) => updateSetting('contact_email', e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="site_description">توضیحات سایت</Label>
              <Textarea
                id="site_description"
                value={settings.site_description}
                onChange={(e) => updateSetting('site_description', e.target.value)}
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* File Upload Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              تنظیمات آپلود فایل
            </CardTitle>
            <CardDescription>
              محدودیت‌ها و تنظیمات مربوط به آپلود فایل
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="max_file_size">حداکثر اندازه فایل (MB)</Label>
                <Input
                  id="max_file_size"
                  type="number"
                  value={settings.max_file_size}
                  onChange={(e) => updateSetting('max_file_size', parseInt(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="allowed_types">انواع فایل مجاز</Label>
                <Input
                  id="allowed_types"
                  value={settings.allowed_file_types.join(', ')}
                  onChange={(e) => updateSetting('allowed_file_types', e.target.value.split(',').map(t => t.trim()))}
                  placeholder="jpg, png, pdf, doc"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              تنظیمات اعلان‌ها
            </CardTitle>
            <CardDescription>
              مدیریت انواع اعلان‌ها و نوتیفیکیشن‌ها
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>اعلان‌های ایمیل</Label>
                <p className="text-sm text-muted-foreground">
                  ارسال اعلان‌ها از طریق ایمیل
                </p>
              </div>
              <Switch
                checked={settings.email_notifications}
                onCheckedChange={(checked) => updateSetting('email_notifications', checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>اعلان‌های پیامک</Label>
                <p className="text-sm text-muted-foreground">
                  ارسال اعلان‌ها از طریق پیامک
                </p>
              </div>
              <Switch
                checked={settings.sms_notifications}
                onCheckedChange={(checked) => updateSetting('sms_notifications', checked)}
              />
            </div>
          </CardContent>
        </Card>

        {/* System Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              تنظیمات سیستم
            </CardTitle>
            <CardDescription>
              تنظیمات امنیتی و عملکرد سیستم
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>حالت تعمیر و نگهداری</Label>
                <p className="text-sm text-muted-foreground">
                  غیرفعال کردن دسترسی کاربران عادی
                </p>
              </div>
              <Switch
                checked={settings.maintenance_mode}
                onCheckedChange={(checked) => updateSetting('maintenance_mode', checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>تأیید خودکار درخواست‌ها</Label>
                <p className="text-sm text-muted-foreground">
                  تأیید خودکار درخواست‌های جدید
                </p>
              </div>
              <Switch
                checked={settings.auto_approval}
                onCheckedChange={(checked) => updateSetting('auto_approval', checked)}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="max_applications">حداکثر درخواست روزانه</Label>
                <Input
                  id="max_applications"
                  type="number"
                  value={settings.max_applications_per_day}
                  onChange={(e) => updateSetting('max_applications_per_day', parseInt(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="session_timeout">زمان انقضای جلسه (دقیقه)</Label>
                <Input
                  id="session_timeout"
                  type="number"
                  value={settings.session_timeout}
                  onChange={(e) => updateSetting('session_timeout', parseInt(e.target.value))}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Password Policy */}
        <Card>
          <CardHeader>
            <CardTitle>سیاست رمز عبور</CardTitle>
            <CardDescription>
              تنظیمات مربوط به قوانین رمز عبور
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="min_length">حداقل طول رمز عبور</Label>
                <Input
                  id="min_length"
                  type="number"
                  value={settings.password_policy.min_length}
                  onChange={(e) => updateSetting('password_policy.min_length', parseInt(e.target.value))}
                />
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>نیاز به کاراکترهای خاص</Label>
                <Switch
                  checked={settings.password_policy.require_special_chars}
                  onCheckedChange={(checked) => updateSetting('password_policy.require_special_chars', checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>نیاز به اعداد</Label>
                <Switch
                  checked={settings.password_policy.require_numbers}
                  onCheckedChange={(checked) => updateSetting('password_policy.require_numbers', checked)}
                />
              </div>
              <div className="flex items-center justify-between">
                <Label>نیاز به حروف بزرگ</Label>
                <Switch
                  checked={settings.password_policy.require_uppercase}
                  onCheckedChange={(checked) => updateSetting('password_policy.require_uppercase', checked)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Backup Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              تنظیمات پشتیبان‌گیری
            </CardTitle>
            <CardDescription>
              مدیریت پشتیبان‌گیری خودکار از داده‌ها
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>پشتیبان‌گیری خودکار</Label>
                <p className="text-sm text-muted-foreground">
                  ایجاد پشتیبان خودکار از داده‌ها
                </p>
              </div>
              <Switch
                checked={settings.backup_settings.auto_backup}
                onCheckedChange={(checked) => updateSetting('backup_settings.auto_backup', checked)}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>فرکانس پشتیبان‌گیری</Label>
                <Select
                  value={settings.backup_settings.backup_frequency}
                  onValueChange={(value) => updateSetting('backup_settings.backup_frequency', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="daily">روزانه</SelectItem>
                    <SelectItem value="weekly">هفتگی</SelectItem>
                    <SelectItem value="monthly">ماهانه</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="retention">مدت نگهداری (روز)</Label>
                <Input
                  id="retention"
                  type="number"
                  value={settings.backup_settings.retention_days}
                  onChange={(e) => updateSetting('backup_settings.retention_days', parseInt(e.target.value))}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <PageNavigation />
      </div>
    </AdminLayout>
  );
}
