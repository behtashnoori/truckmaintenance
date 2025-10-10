/**
 * Test Navigation Page
 * برای تست مسیریابی با نشان
 */

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { NavigationModal } from '@/components/NavigationModal';
import { NavigationService } from '@/services/navigation';
import { testNeshanAPI, testNeshanEndpoints } from '@/utils/neshanTest';
import { MapPin, Navigation2, TestTube, Bug } from 'lucide-react';
import { Header } from '@/components/Header';

export const TestNavigation: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [destLat, setDestLat] = useState('35.7219'); // میدان آزادی تهران
  const [destLon, setDestLon] = useState('51.3347');
  const [providerName, setProviderName] = useState('میدان آزادی تهران');
  const [routeInfo, setRouteInfo] = useState<any>(null);
  const [isTestingAPI, setIsTestingAPI] = useState(false);
  const [apiTestResult, setApiTestResult] = useState<any>(null);
  const [isTestingDirectAPI, setIsTestingDirectAPI] = useState(false);

  const testNeshanAPI = async () => {
    setIsTestingAPI(true);
    setRouteInfo(null);
    
    const userLocation = await NavigationService.getCurrentLocation();
    
    if (!userLocation) {
      alert('لطفاً دسترسی به موقعیت مکانی را فعال کنید');
      setIsTestingAPI(false);
      return;
    }

    const route = await NavigationService.getRoute(
      userLocation.lat,
      userLocation.lon,
      parseFloat(destLat),
      parseFloat(destLon),
      'car'
    );

    setRouteInfo(route);
    setIsTestingAPI(false);
  };

  const testDirectNeshanAPI = async () => {
    setIsTestingDirectAPI(true);
    setApiTestResult(null);
    
    const result = await testNeshanAPI();
    setApiTestResult(result);
    setIsTestingDirectAPI(false);
  };

  const testAllEndpoints = async () => {
    setIsTestingDirectAPI(true);
    setApiTestResult(null);
    
    await testNeshanEndpoints();
    setIsTestingDirectAPI(false);
  };

  const formatDistance = (meters: number): string => {
    const km = meters / 1000;
    if (km < 1) {
      return `${Math.round(meters)} متر`;
    }
    return `${km.toFixed(1)} کیلومتر`;
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours} ساعت ${minutes} دقیقه`;
    }
    return `${minutes} دقیقه`;
  };

  // مکان‌های تست از پیش تعریف شده
  const testLocations = [
    { name: 'میدان آزادی تهران', lat: '35.6997', lon: '51.3381' },
    { name: 'برج میلاد تهران', lat: '35.7447', lon: '51.3753' },
    { name: 'میدان ولیعصر تهران', lat: '35.7051', lon: '51.4177' },
    { name: 'پارک ملت تهران', lat: '35.7336', lon: '51.4281' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header title="تست مسیریابی نشان" />
      
      <div className="container mx-auto p-4 max-w-4xl">
        <Card className="mb-6 border-2 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-800">
              <TestTube className="h-5 w-5" />
              صفحه تست مسیریابی با نشان
            </CardTitle>
            <p className="text-sm text-gray-600 mt-2">
              این صفحه برای تست عملکرد API نشان و مسیریابی طراحی شده است
            </p>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* مختصات مقصد */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                مختصات مقصد
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="lat">عرض جغرافیایی (Latitude)</Label>
                  <Input
                    id="lat"
                    type="text"
                    value={destLat}
                    onChange={(e) => setDestLat(e.target.value)}
                    placeholder="35.7219"
                  />
                </div>
                
                <div>
                  <Label htmlFor="lon">طول جغرافیایی (Longitude)</Label>
                  <Input
                    id="lon"
                    type="text"
                    value={destLon}
                    onChange={(e) => setDestLon(e.target.value)}
                    placeholder="51.3347"
                  />
                </div>
                
                <div>
                  <Label htmlFor="name">نام مقصد</Label>
                  <Input
                    id="name"
                    type="text"
                    value={providerName}
                    onChange={(e) => setProviderName(e.target.value)}
                    placeholder="نام مکان"
                  />
                </div>
              </div>

              {/* مکان‌های پیش‌فرض */}
              <div>
                <Label className="mb-2 block">مکان‌های آزمایشی:</Label>
                <div className="flex flex-wrap gap-2">
                  {testLocations.map((loc) => (
                    <Button
                      key={loc.name}
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setDestLat(loc.lat);
                        setDestLon(loc.lon);
                        setProviderName(loc.name);
                      }}
                    >
                      {loc.name}
                    </Button>
                  ))}
                </div>
              </div>
            </div>

            {/* دکمه‌های تست */}
            <div className="flex gap-3 flex-wrap">
              <Button
                onClick={testNeshanAPI}
                disabled={isTestingAPI}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isTestingAPI ? 'در حال تست API...' : 'تست API نشان'}
              </Button>
              
              <Button
                onClick={testDirectNeshanAPI}
                disabled={isTestingDirectAPI}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <Bug className="h-4 w-4 ml-2" />
                {isTestingDirectAPI ? 'تست مستقیم...' : 'تست مستقیم API'}
              </Button>
              
              <Button
                onClick={testAllEndpoints}
                disabled={isTestingDirectAPI}
                className="bg-orange-600 hover:bg-orange-700"
              >
                <TestTube className="h-4 w-4 ml-2" />
                تست تمام Endpoint ها
              </Button>
              
              <Button
                onClick={() => setIsModalOpen(true)}
                className="bg-green-600 hover:bg-green-700"
              >
                <Navigation2 className="h-4 w-4 ml-2" />
                باز کردن مودال مسیریابی
              </Button>
            </div>

            {/* نتیجه تست API */}
            {routeInfo && (
              <Card className="bg-green-50 border-green-200">
                <CardHeader>
                  <CardTitle className="text-green-800 text-lg">✅ پاسخ API نشان</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white p-3 rounded-md">
                      <p className="text-sm text-gray-600">مسافت</p>
                      <p className="text-xl font-bold text-green-700">
                        {formatDistance(routeInfo.distance)}
                      </p>
                    </div>
                    <div className="bg-white p-3 rounded-md">
                      <p className="text-sm text-gray-600">زمان سفر</p>
                      <p className="text-xl font-bold text-blue-700">
                        {formatDuration(routeInfo.duration)}
                      </p>
                    </div>
                  </div>
                  
                  <details className="bg-white p-3 rounded-md">
                    <summary className="cursor-pointer font-medium text-gray-700">
                      مشاهده JSON کامل
                    </summary>
                    <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto max-h-64">
                      {JSON.stringify(routeInfo, null, 2)}
                    </pre>
                  </details>
                </CardContent>
              </Card>
            )}

            {/* نتیجه تست مستقیم API */}
            {apiTestResult && (
              <Card className={`${apiTestResult.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                <CardHeader>
                  <CardTitle className={`${apiTestResult.success ? 'text-green-800' : 'text-red-800'} text-lg`}>
                    {apiTestResult.success ? '✅ تست مستقیم API موفق' : '❌ تست مستقیم API ناموفق'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <pre className="text-xs bg-white p-3 rounded overflow-auto max-h-64">
                    {JSON.stringify(apiTestResult, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            )}

            {routeInfo === null && isTestingAPI === false && !apiTestResult && (
              <div className="bg-gray-100 p-4 rounded-md text-center text-gray-600">
                روی یکی از دکمه‌های تست کلیک کنید تا API نشان را بررسی کنید
              </div>
            )}
          </CardContent>
        </Card>

        {/* راهنما */}
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <CardTitle className="text-yellow-800">📋 راهنمای استفاده</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-gray-700">
            <p>1️⃣ مختصات مقصد را وارد کنید یا یکی از مکان‌های پیش‌فرض را انتخاب کنید</p>
            <p>2️⃣ برای تست API نشان، روی دکمه "تست API نشان" کلیک کنید</p>
            <p>3️⃣ برای باز کردن مودال مسیریابی، روی "باز کردن مودال مسیریابی" کلیک کنید</p>
            <p>4️⃣ اطمینان حاصل کنید که دسترسی به موقعیت مکانی در مرورگر فعال است</p>
            <p className="mt-3 p-2 bg-white rounded border border-yellow-300">
              <strong>کلید API نشان:</strong> service.d39f79de30c34282b0a48564ff3b8b13
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Navigation Modal */}
      <NavigationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        providerLocation={{
          lat: parseFloat(destLat),
          lon: parseFloat(destLon)
        }}
        providerName={providerName}
      />
    </div>
  );
};

export default TestNavigation;

