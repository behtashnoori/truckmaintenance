import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { Upload, Download, FileSpreadsheet, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';

interface UploadResult {
  success: boolean;
  message: string;
  details?: {
    total: number;
    success: number;
    failed: number;
    errors: string[];
  };
}

export const BulkUpload: React.FC = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
          file.type === 'application/vnd.ms-excel') {
        setSelectedFile(file);
        setUploadResult(null);
      } else {
        toast({
          title: 'خطا',
          description: 'لطفاً فایل اکسل معتبر انتخاب کنید.',
          variant: 'destructive',
        });
      }
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/business-expert/providers/template');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'template_providers.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast({
          title: 'قالب دانلود شد',
          description: 'فایل قالب با موفقیت دانلود شد.',
        });
      } else {
        throw new Error('خطا در دانلود قالب');
      }
    } catch (error) {
      console.error('Error downloading template:', error);
      toast({
        title: 'خطا',
        description: 'خطا در دانلود قالب. لطفاً دوباره تلاش کنید.',
        variant: 'destructive',
      });
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('/api/business-expert/providers/bulk-upload', {
        method: 'POST',
        body: formData,
      });

      const result: UploadResult = await response.json();

      if (result.success) {
        setUploadResult(result);
        toast({
          title: 'آپلود موفق',
          description: result.message,
        });
        setSelectedFile(null);
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        setUploadResult(result);
        toast({
          title: 'خطا در آپلود',
          description: result.message,
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast({
        title: 'خطا',
        description: 'خطا در آپلود فایل. لطفاً دوباره تلاش کنید.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

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
          
          <h1 className="text-3xl font-bold text-foreground mb-2">
            آپلود انبوه ارائه‌دهندگان
          </h1>
          <p className="text-muted-foreground">
            فایل اکسل حاوی اطلاعات ارائه‌دهندگان را آپلود کنید
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* دانلود قالب */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download size={20} />
                دانلود قالب فایل
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                ابتدا قالب فایل اکسل را دانلود کنید و اطلاعات ارائه‌دهندگان را در آن وارد کنید.
              </p>
              
              <Button
                onClick={handleDownloadTemplate}
                className="w-full"
                variant="outline"
              >
                <FileSpreadsheet className="w-4 h-4 mr-2" />
                دانلود قالب اکسل
              </Button>

              <div className="text-xs text-muted-foreground space-y-1">
                <p><strong>نکات مهم:</strong></p>
                <ul className="list-disc list-inside space-y-1">
                  <li>فقط فایل‌های اکسل (.xlsx, .xls) قابل قبول است</li>
                  <li>ستون‌های الزامی را حتماً پر کنید</li>
                  <li>فرمت شماره موبایل: 09123456789</li>
                  <li>مختصات جغرافیایی باید عدد معتبر باشند</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* آپلود فایل */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload size={20} />
                آپلود فایل
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="w-full"
                >
                  <FileSpreadsheet className="w-4 h-4 mr-2" />
                  {selectedFile ? selectedFile.name : 'انتخاب فایل اکسل'}
                </Button>
              </div>

              {selectedFile && (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-sm">
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>{selectedFile.name}</span>
                    <span className="text-muted-foreground">
                      ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </span>
                  </div>

                  {isUploading && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>در حال آپلود...</span>
                        <span>{uploadProgress}%</span>
                      </div>
                      <Progress value={uploadProgress} />
                    </div>
                  )}

                  <Button
                    onClick={handleUpload}
                    disabled={isUploading}
                    className="w-full"
                  >
                    {isUploading ? 'در حال آپلود...' : 'آپلود فایل'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* نتایج آپلود */}
        {uploadResult && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {uploadResult.success ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-500" />
                )}
                نتایج آپلود
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Alert className={uploadResult.success ? 'border-green-200' : 'border-red-200'}>
                <AlertDescription>
                  {uploadResult.message}
                </AlertDescription>
              </Alert>

              {uploadResult.details && (
                <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {uploadResult.details.total}
                    </div>
                    <div className="text-muted-foreground">کل رکوردها</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {uploadResult.details.success}
                    </div>
                    <div className="text-muted-foreground">موفق</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {uploadResult.details.failed}
                    </div>
                    <div className="text-muted-foreground">ناموفق</div>
                  </div>
                </div>
              )}

              {uploadResult.details?.errors && uploadResult.details.errors.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold text-sm mb-2">خطاهای موجود:</h4>
                  <div className="bg-red-50 p-3 rounded-md max-h-32 overflow-y-auto">
                    {uploadResult.details.errors.map((error, index) => (
                      <div key={index} className="text-xs text-red-600 mb-1">
                        • {error}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};
