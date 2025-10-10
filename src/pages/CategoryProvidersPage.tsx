import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { ProviderCard } from '@/components/ProviderCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api, ProviderSearchResult } from '@/lib/api';
import { LoaderCircle, Building, MapPin, Phone } from 'lucide-react';

export const CategoryProvidersPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  
  const [providers, setProviders] = useState<ProviderSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryName, setCategoryName] = useState<string>('');

  useEffect(() => {
    if (slug) {
      fetchCategoryProviders();
    }
  }, [slug]);

  const fetchCategoryProviders = async () => {
    if (!slug) return;

    setIsLoading(true);
    setError(null);

    try {
      // Convert slug back to category name
      const categoryName = slug.replace(/-/g, ' ');
      setCategoryName(categoryName);

      // Use fetch directly to avoid api wrapper issues
      const params = new URLSearchParams({
        lat: '35.6892',
        lon: '51.3890',
        category: categoryName
      });

      const response = await fetch(`/api/public/providers?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.success && data.data) {
          setProviders(data.data);
        } else {
          setError(data.error || 'خطا در بارگذاری نتایج');
        }
      } else {
        setError('خطا در ارتباط با سرور');
      }
    } catch (err) {
      console.error('Error fetching providers:', err);
      setError('خطا در ارتباط با سرور');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderClick = (providerId: number) => {
    navigate(`/provider/${providerId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title={`خدمات ${categoryName}`} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <LoaderCircle className="animate-spin mx-auto mb-4" size={32} />
            <p className="text-muted-foreground">در حال بارگذاری...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header title={`خدمات ${categoryName}`} />
        <div className="flex-1 flex items-center justify-center p-6">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-center text-red-600">خطا</CardTitle>
              <CardDescription className="text-center">{error}</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <Button onClick={fetchCategoryProviders} variant="outline">
                تلاش مجدد
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header title={`خدمات ${categoryName}`} backTo="services" />

      {/* Results */}
      <div className="flex-1 p-4">
        {providers.length === 0 ? (
          <div className="text-center py-8">
            <Building className="h-12 w-12 text-blue-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2 text-blue-600">هنوز در این حوزه ثبت‌نامی انجام نشده</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              در حال حاضر هیچ ارائه‌دهنده‌ای برای خدمات <strong>{categoryName}</strong> ثبت‌نام نکرده است.
              <br />
              شما می‌توانید اولین ارائه‌دهنده در این حوزه باشید!
            </p>
            <div className="space-y-3">
              <Button
                onClick={() => navigate('/signup')}
                className="bg-green-600 hover:bg-green-700 text-white"
                size="lg"
              >
                🚀 ثبت‌نام به عنوان ارائه‌دهنده
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground mb-4">
              {providers.length} ارائه‌دهنده برای خدمات {categoryName} یافت شد
            </div>
            
            {providers && providers.length > 0 ? providers.map((provider) => (
              <div
                key={provider.id}
                onClick={() => handleProviderClick(provider.id)}
                className="cursor-pointer"
              >
                <ProviderCard provider={provider} />
              </div>
            )) : (
              <div className="text-center py-4">
                <p className="text-gray-500">هیچ ارائه‌دهنده‌ای یافت نشد</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
