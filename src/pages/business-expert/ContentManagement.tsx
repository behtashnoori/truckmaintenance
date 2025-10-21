import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/utils/api';
import BusinessExpertLayout from '@/components/business-expert/BusinessExpertLayout';
import { 
  FileText, 
  Phone, 
  Info, 
  Save, 
  Eye, 
  Edit3,
  ArrowLeft,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface ContentData {
  [key: string]: string;
}

interface ContentItem {
  id: number;
  section_key: string;
  content: string;
  is_active: boolean;
  updated_at: string;
  updated_by: number;
}

interface ContentByType {
  [contentType: string]: ContentItem[];
}

const ContentManagement: React.FC = () => {
  const [contentData, setContentData] = useState<ContentByType>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('contact');
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    loadContentData();
  }, []);

  const loadContentData = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/business-expert/content');
      
      if (response.success) {
        setContentData(response.data);
      } else {
        throw new Error(response.error || 'خطا در دریافت محتوا');
      }
    } catch (error) {
      console.error('Error loading content:', error);
      toast({
        title: "خطا در بارگذاری",
        description: "خطا در دریافت محتوا. لطفاً دوباره تلاش کنید.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleContentChange = (contentType: string, sectionKey: string, value: string) => {
    setContentData(prev => ({
      ...prev,
      [contentType]: prev[contentType]?.map(item => 
        item.section_key === sectionKey 
          ? { ...item, content: value }
          : item
      ) || []
    }));
  };

  const handleStatusChange = (contentType: string, sectionKey: string, isActive: boolean) => {
    setContentData(prev => ({
      ...prev,
      [contentType]: prev[contentType]?.map(item => 
        item.section_key === sectionKey 
          ? { ...item, is_active: isActive }
          : item
      ) || []
    }));
  };

  const saveContent = async (contentType: string) => {
    try {
      setSaving(true);
      
      const updates = contentData[contentType]?.map(item => ({
        id: item.id,
        content: item.content,
        is_active: item.is_active
      })) || [];

      const response = await apiFetch('/api/business-expert/content/bulk-update', {
        method: 'PUT',
        body: JSON.stringify({ updates })
      });

      if (response.success) {
        toast({
          title: "ذخیره موفق",
          description: `محتوای ${contentType === 'contact' ? 'تماس با ما' : 'پشتیبانی'} با موفقیت ذخیره شد`,
        });
      } else {
        throw new Error(response.error || 'خطا در ذخیره');
      }
    } catch (error) {
      console.error('Error saving content:', error);
      toast({
        title: "خطا در ذخیره",
        description: "خطا در ذخیره محتوا. لطفاً دوباره تلاش کنید.",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const renderContentForm = (contentType: string, items: ContentItem[]) => {
    return (
      <div className="space-y-6">
        {items.map((item) => (
          <Card key={item.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CardTitle className="text-lg">
                    {getSectionTitle(item.section_key)}
                  </CardTitle>
                  <Badge variant={item.is_active ? "default" : "secondary"}>
                    {item.is_active ? "فعال" : "غیرفعال"}
                  </Badge>
                </div>
                <Switch
                  checked={item.is_active}
                  onCheckedChange={(checked) => handleStatusChange(contentType, item.section_key, checked)}
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
                  <Textarea
                    id={`content-${item.id}`}
                    value={item.content}
                    onChange={(e) => handleContentChange(contentType, item.section_key, e.target.value)}
                    className="min-h-[100px]"
                    placeholder="محتوای این بخش را وارد کنید..."
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={() => navigate('/business-expert/dashboard')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            بازگشت
          </Button>
          <Button
            onClick={() => saveContent(contentType)}
            disabled={saving}
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
    );
  };

  const getSectionTitle = (sectionKey: string): string => {
    const titles: { [key: string]: string } = {
      'hero_title': 'عنوان اصلی',
      'hero_description': 'توضیحات اصلی',
      'contact_email': 'ایمیل تماس',
      'contact_phone': 'تلفن تماس',
      'contact_address': 'آدرس',
      'contact_hours': 'ساعات کاری',
      'support_title': 'عنوان پشتیبانی',
      'support_description': 'توضیحات پشتیبانی',
      'support_email': 'ایمیل پشتیبانی',
      'support_phone': 'تلفن پشتیبانی',
      'support_hours': 'ساعات پشتیبانی'
    };
    return titles[sectionKey] || sectionKey;
  };

  if (loading) {
    return (
      <BusinessExpertLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">در حال بارگذاری محتوا...</p>
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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">مدیریت محتوا</h1>
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              مدیریت محتوای صفحات تماس با ما و پشتیبانی
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Button 
              onClick={() => navigate('/business-expert/dashboard')}
              variant="outline"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              بازگشت به داشبورد
            </Button>
          </div>
        </div>

        {/* Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="contact" className="flex items-center gap-2">
              <Phone className="h-4 w-4" />
              تماس با ما
            </TabsTrigger>
            <TabsTrigger value="about" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              درباره ما
            </TabsTrigger>
          </TabsList>

          <TabsContent value="contact" className="mt-6">
            {contentData.contact ? (
              renderContentForm('contact', contentData.contact)
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <Phone className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-muted-foreground">محتوای "تماس با ما" یافت نشد</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="about" className="mt-6">
            {contentData.about ? (
              renderContentForm('about', contentData.about)
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-muted-foreground">محتوای "درباره ما" یافت نشد</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </BusinessExpertLayout>
  );
};

export default ContentManagement;
