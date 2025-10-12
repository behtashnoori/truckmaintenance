/**
 * Navigation Modal Component
 * Neshan-only navigation with real-time route information
 */

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { X, MapPin, Clock, Route, Navigation2 } from 'lucide-react';
import { NavigationService, RouteResponse } from '@/services/navigation';
import NESHAN_CONFIG from '@/config/neshan';

interface NavigationModalProps {
  isOpen: boolean;
  onClose: () => void;
  providerLocation: { lat: number; lon: number };
  providerName: string;
}

export const NavigationModal: React.FC<NavigationModalProps> = ({
  isOpen,
  onClose,
  providerLocation,
  providerName
}) => {
  const { lat, lon } = providerLocation;
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [routeInfo, setRouteInfo] = useState<RouteResponse | null>(null);
  const [isLoadingRoute, setIsLoadingRoute] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  // Get user location and route info when modal opens
  useEffect(() => {
    if (isOpen) {
      const loadRouteInfo = async () => {
        console.log('🚀 NavigationModal: Starting location request...');
        setLocationError(null);
        
        try {
          const location = await NavigationService.getCurrentLocation();
          console.log('📍 NavigationModal: Location result:', location);
          
          if (location) {
            setUserLocation(location);
            setIsLoadingRoute(true);
            setLocationError(null);
            
            console.log('🗺️ Loading route info for:', {
              from: `${location.lat},${location.lon}`,
              to: `${lat},${lon}`
            });
            
            // Get real route from Neshan API
            const route = await NavigationService.getRoute(
              location.lat,
              location.lon,
              lat,
              lon
            );
            
            console.log('📊 Route info received:', route);
            
            // If API didn't return valid data, use fallback calculation
            if (!route || !route.distance || !route.duration) {
              console.log('⚠️ API returned invalid data, using fallback calculation...');
              const fallbackDistance = NavigationService.calculateDistance(
                location.lat, location.lon, lat, lon
              ) * 1000; // Convert to meters
              const fallbackDuration = Math.round(fallbackDistance / 1000 * 60); // 1km per minute
              
              const fallbackRoute = {
                distance: fallbackDistance,
                duration: fallbackDuration,
                legs: [{
                  distance: fallbackDistance,
                  duration: fallbackDuration,
                  steps: []
                }]
              };
              
              console.log('✅ Using fallback route:', fallbackRoute);
              setRouteInfo(fallbackRoute);
            } else {
              console.log('✅ Using API route:', route);
              setRouteInfo(route);
            }
          } else {
            console.warn('❌ User location not available - permission denied or error occurred');
            setUserLocation(null);
            setRouteInfo(null);
            setLocationError('دسترسی به موقعیت مکانی رد شد یا خطا رخ داد');
          }
        } catch (error) {
          console.error('💥 Error loading route info:', error);
          setRouteInfo(null);
          setLocationError('خطا در دریافت موقعیت مکانی');
        } finally {
          setIsLoadingRoute(false);
        }
      };
      
      loadRouteInfo();
    } else {
      // Reset state when modal closes
      console.log('🔄 NavigationModal: Resetting state...');
      setUserLocation(null);
      setRouteInfo(null);
      setIsLoadingRoute(false);
      setLocationError(null);
    }
  }, [isOpen, lat, lon]);

  const handleOpenNeshan = async () => {
    await NavigationService.openNeshan({ 
      lat, 
      lon, 
      label: providerName, 
      originLat: userLocation?.lat, 
      originLon: userLocation?.lon 
    });
    onClose();
  };

  // تشخیص نوع دستگاه برای نمایش پیام مناسب
  const isMobile = NavigationService.isMobileDevice();
  const deviceInfo = isMobile 
    ? 'باز می‌شود در اپلیکیشن نشان (اگر نصب باشد)'
    : 'باز می‌شود در مرورگر';
  
  const buttonText = isMobile
    ? 'باز کردن در اپلیکیشن نشان'
    : 'مسیریابی با نشان';

  // تابع تلاش مجدد برای دریافت موقعیت
  const retryLocation = async () => {
    console.log('🔄 Retrying location request...');
    setLocationError(null);
    setUserLocation(null);
    setRouteInfo(null);
    
    const location = await NavigationService.getCurrentLocation();
    if (location) {
      setUserLocation(location);
      // محاسبه مسیر با موقعیت جدید
      const fallbackDistance = NavigationService.calculateDistance(
        location.lat, location.lon, lat, lon
      ) * 1000;
      const fallbackDuration = Math.round(fallbackDistance / 1000 * 60);
      
      const fallbackRoute = {
        distance: fallbackDistance,
        duration: fallbackDuration,
        legs: [{
          distance: fallbackDistance,
          duration: fallbackDuration,
          steps: []
        }]
      };
      
      setRouteInfo(fallbackRoute);
    } else {
      setLocationError('دسترسی به موقعیت مکانی رد شد');
    }
  };

  const formatDistance = (meters: number): string => {
    // بررسی کنید که مقدار معتبر باشد
    if (!meters || isNaN(meters) || meters <= 0) {
      return 'نامشخص';
    }
    
    const km = meters / 1000;
    if (km < 1) {
      return `${Math.round(meters)} متر`;
    }
    return `${km.toFixed(1)} کیلومتر`;
  };

  const formatDuration = (seconds: number): string => {
    // بررسی کنید که مقدار معتبر باشد
    if (!seconds || isNaN(seconds) || seconds <= 0) {
      return 'نامشخص';
    }
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours} ساعت ${minutes} دقیقه`;
    }
    return `${minutes} دقیقه`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <Card className="w-full max-w-md mx-4 shadow-2xl border-2 border-green-200">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="text-xl font-bold text-green-800 flex items-center gap-2">
              <Navigation2 className="h-5 w-5" />
              مسیریابی با نشان
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0 hover:bg-red-50"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            مسیریابی به <strong>{providerName}</strong>
          </p>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Route Information from Neshan API */}
          {isLoadingRoute && (
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 text-center">
              <p className="text-sm text-blue-700">در حال دریافت اطلاعات مسیر...</p>
            </div>
          )}

          {!isLoadingRoute && routeInfo && (
            <div className="bg-gradient-to-br from-green-50 to-blue-50 p-4 rounded-lg border border-green-200">
              <div className="flex items-center gap-2 mb-3">
                <Route className="h-5 w-5 text-green-600" />
                <span className="text-sm font-bold text-green-800">اطلاعات مسیر (نشان)</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-3 rounded-md">
                  <div className="flex items-center gap-2 mb-1">
                    <MapPin className="h-4 w-4 text-green-600" />
                    <span className="text-xs text-gray-600">مسافت</span>
                  </div>
                  <p className="text-lg font-bold text-green-700">
                    {formatDistance(routeInfo.distance || routeInfo.legs?.[0]?.distance || 0)}
                  </p>
                </div>
                <div className="bg-white p-3 rounded-md">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="h-4 w-4 text-blue-600" />
                    <span className="text-xs text-gray-600">زمان تقریبی</span>
                  </div>
                  <p className="text-lg font-bold text-blue-700">
                    {formatDuration(routeInfo.duration || routeInfo.legs?.[0]?.duration || 0)}
                  </p>
                </div>
              </div>
              
              {/* Debug info - برای تست */}
              <details className="mt-3">
                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                  🔍 Debug: ساختار داده دریافتی
                </summary>
                <div className="mt-2 p-2 bg-white rounded border text-xs">
                  <pre className="overflow-auto max-h-32 whitespace-pre-wrap">
                    {JSON.stringify(routeInfo, null, 2)}
                  </pre>
                </div>
              </details>
            </div>
          )}

          {!isLoadingRoute && !routeInfo && userLocation && (
            <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
              <p className="text-sm text-yellow-700 text-center">
                امکان دریافت اطلاعات مسیر وجود ندارد. مسیریابی بدون اطلاعات تفصیلی انجام می‌شود.
              </p>
              <details className="mt-2">
                <summary className="text-xs text-yellow-600 cursor-pointer">مشاهده جزئیات خطا</summary>
                <div className="mt-2 p-2 bg-white rounded text-xs text-gray-600">
                  <p>مبدا: {userLocation.lat.toFixed(6)}, {userLocation.lon.toFixed(6)}</p>
                  <p>مقصد: {lat.toFixed(6)}, {lon.toFixed(6)}</p>
                  <p>کلید API: {NESHAN_CONFIG.API_KEY.substring(0, 15)}...</p>
                </div>
              </details>
            </div>
          )}

          {!isLoadingRoute && !routeInfo && !userLocation && (
            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <div className="text-center">
                <p className="text-sm text-red-700 mb-3">
                  {locationError || 'دسترسی به موقعیت مکانی امکان‌پذیر نیست. لطفاً دسترسی موقعیت را در مرورگر فعال کنید.'}
                </p>
                
                <div className="space-y-2">
                  <Button 
                    onClick={retryLocation}
                    variant="outline"
                    size="sm"
                    className="w-full border-red-300 text-red-700 hover:bg-red-50"
                  >
                    🔄 تلاش مجدد
                  </Button>
                  
                  <p className="text-xs text-red-600">
                    💡 راهنمای رفع مشکل:<br/>
                    • روی آیکون قفل کنار آدرس کلیک کنید<br/>
                    • "موقعیت مکانی" را روی "مجاز" تنظیم کنید<br/>
                    • صفحه را refresh کنید
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Device Info */}
          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-700 text-center">
              📱 {deviceInfo}
            </p>
          </div>

          {/* Neshan Navigation Button */}
          <Button
            onClick={handleOpenNeshan}
            className="w-full h-14 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold text-lg shadow-lg hover:shadow-xl transition-all"
            disabled={false} // همیشه فعال باشه
          >
            <Navigation2 className="h-5 w-5 ml-2" />
            {userLocation ? buttonText : 'مسیریابی به مقصد'}
          </Button>

          {!userLocation && (
            <p className="text-xs text-center text-gray-500">
              ⚠️ بدون موقعیت فعلی، فقط مقصد در نشان نمایش داده می‌شود
            </p>
          )}

          {/* Close Button */}
          <div className="pt-2 border-t">
            <Button
              onClick={onClose}
              variant="ghost"
              className="w-full hover:bg-gray-50"
            >
              انصراف
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default NavigationModal;
