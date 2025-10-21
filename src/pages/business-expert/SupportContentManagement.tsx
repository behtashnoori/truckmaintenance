import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';
import BusinessExpertLayout from '@/components/business-expert/BusinessExpertLayout';
import { 
  FileText, 
  Save, 
  ArrowLeft,
  Mail,
  Phone,
  Clock,
  Info,
  MessageCircle
} from 'lucide-react';

interface ContentItem {
  id: number;
  section_key: string;
  content: string;
  is_active: boolean;
  updated_at: string;
  updated_by: number;
}

const AboutContentManagement: React.FC = () => {
  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    loadAboutContent();
  }, []);

  const loadAboutContent = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/business-expert/content/about');
      
      if (response.success) {
        setContentItems(response.data);
      } else {
        throw new Error(response.error || 'خطا در دریافت محتوا');
      }
    } catch (error) {
      console.error('Error loading about content:', error);
      toast({
        title: "خطا در بارگذاری",
        description: "خطا در دریافت محتوای درباره. لطفاً دوباره تلاش کنید.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (sectionKey: string, value: string) => {
    setContentItems(prev => 
      prev.map(item => 
        item.section_key === sectionKey 
          ? { ...item, content: value }
          : item
      )
    );
  };

  const handleStatusChange = (sectionKey: string, isActive: boolean) => {
    setContentItems(prev => 
      prev.map(item => 
        item.section_key === sectionKey 
          ? { ...item, is_active: isActive }
          : item
      )
    );
  };

  const saveContent = async () => {
    try {
      setSaving(true);
      
      const updates = contentItems.map(item => ({
        id: item.id,
        content: item.content,
        is_active: item.is_active
      }));

      const response = await apiFetch('/api/business-expert/content/bulk-update', {
        method: 'PUT',
        body: JSON.stringify({ updates })
      });

      if (response.success) {
        toast({
          title: "ذخیره موفق",
          description: "محتوای صفحه درباره با موفقیت ذخیره شد",
        });
      } else {
        throw new Error(response.error || 'خطا در ذخیره');
      }
    } catch (error) {
      console.error('Error saving about content:', error);
      toast({
        title: "خطا در ذخیره",
        description: "خطا در ذخیره محتوا. لطفاً دوباره تلاش کنید.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const getSectionTitle = (sectionKey: string): string => {
    const titles: { [key: string]: string } = {
      'about_title': 'عنوان اصلی درباره',
      'about_description': 'توضیحات درباره',
      'about_mission': 'ماموریت ما',
      'about_vision': 'چشم‌انداز ما',
      'about_values': 'ارزش‌های ما',
      'about_history': 'تاریخچه',
      'about_team': 'تیم ما',
      'about_achievements': 'دستاوردها',
      'about_contact': 'اطلاعات تماس',
      'about_address': 'آدرس'
    };
    return titles[sectionKey] || sectionKey;
  };

  const getSectionIcon = (sectionKey: string) => {
    if (sectionKey.includes('email')) return <Mail className="h-4 w-4" />;
    if (sectionKey.includes('phone')) return <Phone className="h-4 w-4" />;
    if (sectionKey.includes('address')) return <Clock className="h-4 w-4" />;
    if (sectionKey.includes('mission') || sectionKey.includes('vision')) return <Info className="h-4 w-4" />;
    if (sectionKey.includes('team')) return <MessageCircle className="h-4 w-4" />;
    return <FileText className="h-4 w-4" />;
  };

  if (loading) {
    return (
      <BusinessExpertLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">در حال بارگذاری محتوای درباره...</p>
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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <FileText className="h-6 w-6" />
              مدیریت محتوای درباره ما
            </h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              مدیریت محتوای صفحه درباره ما
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex gap-2">
            <Button 
              onClick={() => navigate('/business-expert/content')}
              variant="outline"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              بازگشت
            </Button>
            <Button 
              onClick={() => navigate('/business-expert/dashboard')}
              variant="outline"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              داشبورد
            </Button>
          </div>
        </div>

        {/* Content Items */}
        <div className="space-y-6">
          {contentItems.map((item) => (
            <Card key={item.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getSectionIcon(item.section_key)}
                    <CardTitle className="text-lg">
                      {getSectionTitle(item.section_key)}
                    </CardTitle>
                    <Badge variant={item.is_active ? "default" : "secondary"}>
                      {item.is_active ? "فعال" : "غیرفعال"}
                    </Badge>
                  </div>
                  <Switch
                    checked={item.is_active}
                    onCheckedChange={(checked) => handleStatusChange(item.section_key, checked)}
                  />
                </div>
                <CardDescription>
                  آخرین بروزرسانی: {new Date(item.updated_at).toLocaleDateString('fa-IR')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor={`content-${item.id}`}>
                      محتوا
                    </Label>
                    {item.section_key.includes('description') || item.section_key.includes('address') ? (
                      <Textarea
                        id={`content-${item.id}`}
                        value={item.content}
                        onChange={(e) => handleContentChange(item.section_key, e.target.value)}
                        className="min-h-[100px]"
                        placeholder="محتوای این بخش را وارد کنید..."
                      />
                    ) : (
                      <Input
                        id={`content-${item.id}`}
                        value={item.content}
                        onChange={(e) => handleContentChange(item.section_key, e.target.value)}
                        placeholder="محتوای این بخش را وارد کنید..."
                      />
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {/* Save Button */}
        <div className="flex justify-end">
          <Button
            onClick={saveContent}
            disabled={saving}
            size="lg"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                در حال ذخیره...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                ذخیره تغییرات
              </>
            )}
          </Button>
        </div>
      </div>
    </BusinessExpertLayout>
  );
};

export default AboutContentManagement;
