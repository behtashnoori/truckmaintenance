import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Save, RefreshCw, FileText, Phone } from 'lucide-react';
import { apiFetch } from '@/utils/api';
import { toast } from '@/hooks/use-toast';
import AdminLayout from '@/components/admin/AdminLayout';
import { convertToPersianNumbers, convertToEnglishNumbers } from '@/utils/persianNumbers';

interface ContentItem {
  id: number;
  section_key: string;
  content: string;
  is_active: boolean;
  updated_at?: string;
  updated_by?: number;
}

interface ContentData {
  [contentType: string]: ContentItem[];
}

const ContentManagement: React.FC = () => {
  const [contentData, setContentData] = useState<ContentData>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('about');

  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    try {
      setLoading(true);
      const response = await apiFetch('/api/admin/content');
      if (response.success) {
        // Convert English numbers to Persian for display
        const convertedData: ContentData = {};
        Object.keys(response.data).forEach(contentType => {
          convertedData[contentType] = response.data[contentType].map((item: ContentItem) => ({
            ...item,
            content: convertToPersianNumbers(item.content || '')
          }));
        });
        setContentData(convertedData);
      } else {
        toast({
          title: "خطا",
          description: "خطا در بارگذاری محتوا",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error loading content:', error);
      toast({
        title: "خطا",
        description: "خطا در بارگذاری محتوا",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };


  const handleContentChange = (contentType: string, itemId: number, field: string, value: any) => {
    setContentData(prev => ({
      ...prev,
      [contentType]: prev[contentType]?.map(item => 
        item.id === itemId 
          ? { ...item, [field]: value }
          : item
      ) || []
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Prepare updates for all content
      const updates: any[] = [];
      
      Object.values(contentData).forEach(contentItems => {
        contentItems.forEach(item => {
          updates.push({
            id: item.id,
            content: convertToEnglishNumbers(item.content || ''), // Convert Persian numbers to English for API
            is_active: item.is_active
          });
        });
      });

      const response = await apiFetch('/api/admin/content/bulk-update', {
        method: 'PUT',
        body: JSON.stringify({ updates })
      });

      if (response.success) {
        toast({
          title: "موفق",
          description: response.message || "محتوای با موفقیت ذخیره شد",
        });
        await loadContent(); // Reload to get fresh data
      } else {
        toast({
          title: "خطا",
          description: "خطا در ذخیره محتوا",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error saving content:', error);
      toast({
        title: "خطا",
        description: "خطا در ذخیره محتوا",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  const getFieldLabel = (sectionKey: string): string => {
    const labels: { [key: string]: string } = {
      hero_title: 'عنوان اصلی',
      hero_subtitle: 'زیرعنوان',
      mission_text: 'متن ماموریت',
      team_text: 'متن تیم',
      feature_security: 'ویژگی امنیت',
      feature_coverage: 'ویژگی پوشش سراسری',
      feature_quality: 'ویژگی کیفیت',
      feature_expertise: 'ویژگی تخصص',
      contact_phone: 'شماره تلفن',
      contact_email: 'ایمیل',
      contact_address: 'آدرس',
      contact_postal_code: 'کدپستی',
      working_hours_weekday: 'ساعات کاری شنبه-پنجشنبه',
      working_hours_friday: 'ساعات کاری جمعه',
    };
    return labels[sectionKey] || sectionKey;
  };

  const renderContentForm = (contentType: string, contentItems: ContentItem[]) => {
    return (
      <div className="space-y-6">
        {contentItems.map((item) => (
          <Card key={item.id}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{getFieldLabel(item.section_key)}</CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant={item.is_active ? "default" : "secondary"}>
                    {item.is_active ? "فعال" : "غیرفعال"}
                  </Badge>
                  <Switch
                    checked={item.is_active}
                    onCheckedChange={(checked) => 
                      handleContentChange(contentType, item.id, 'is_active', checked)
                    }
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {item.section_key.includes('text') || item.section_key === 'contact_address' ? (
                <Textarea
                  value={item.content || ''}
                  onChange={(e) => 
                    handleContentChange(contentType, item.id, 'content', convertToPersianNumbers(e.target.value))
                  }
                  rows={4}
                  placeholder="محتوای متن را وارد کنید..."
                  className="font-farsi"
                />
              ) : (
                <Input
                  value={item.content || ''}
                  onChange={(e) => 
                    handleContentChange(contentType, item.id, 'content', convertToPersianNumbers(e.target.value))
                  }
                  placeholder="محتوای فیلد را وارد کنید..."
                  className="font-farsi"
                />
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    );
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
            <h1 className="text-3xl font-bold">مدیریت محتوا</h1>
            <p className="text-muted-foreground">
              مدیریت محتوای صفحات "درباره ما" و "تماس با ما"
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={loadContent}>
              <RefreshCw className="h-4 w-4 mr-2" />
              بروزرسانی
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'در حال ذخیره...' : 'ذخیره تغییرات'}
            </Button>
          </div>
        </div>

        {/* Content Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="about" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              درباره ما
            </TabsTrigger>
            <TabsTrigger value="contact" className="flex items-center gap-2">
              <Phone className="h-4 w-4" />
              تماس با ما
            </TabsTrigger>
          </TabsList>

          <TabsContent value="about" className="mt-6">
            {contentData.about ? (
              renderContentForm('about', contentData.about)
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-muted-foreground">محتوای "درباره ما" یافت نشد</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="contact" className="mt-6">
            {contentData.contact ? (
              renderContentForm('contact', contentData.contact)
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <p className="text-muted-foreground">محتوای "تماس با ما" یافت نشد</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </AdminLayout>
  );
};

export default ContentManagement;
