/**
 * Navigation Service
 * Handles navigation using Neshan Map API
 */

import NESHAN_CONFIG from '@/config/neshan';

export interface NavigationOptions {
  lat: number; // Destination latitude
  lon: number; // Destination longitude
  label?: string; // Destination label
  originLat?: number; // User's current latitude
  originLon?: number; // User's current longitude
}

export interface RouteResponse {
  distance: number; // Distance in meters
  duration: number; // Duration in seconds
  legs: Array<{
    distance: number;
    duration: number;
    steps: Array<{
      name: string;
      instruction: string;
      distance: number;
      duration: number;
    }>;
  }>;
}

export class NavigationService {
  /**
   * Check if the device is a mobile device
   */
  static isMobileDevice(): boolean {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    );
  }

  /**
   * Check if the device is iOS
   */
  static isIOS(): boolean {
    return /iPad|iPhone|iPod/.test(navigator.userAgent);
  }

  /**
   * Check if the device is Android
   */
  static isAndroid(): boolean {
    return /Android/.test(navigator.userAgent);
  }

  /**
   * Get route information from Neshan API
   */
  static async getRoute(
    originLat: number,
    originLon: number,
    destLat: number,
    destLon: number,
    type: 'car' | 'motorcycle' | 'taxi' = 'car'
  ): Promise<RouteResponse | null> {
    try {
      // Use correct Neshan API endpoint
      const url = `${NESHAN_CONFIG.API_BASE_URL}/direction?type=${type}&origin=${originLat},${originLon}&destination=${destLat},${destLon}`;
      
      console.log('Neshan API Request:', {
        url,
        apiKey: NESHAN_CONFIG.API_KEY.substring(0, 10) + '...',
        origin: `${originLat},${originLon}`,
        destination: `${destLat},${destLon}`
      });
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Api-Key': NESHAN_CONFIG.API_KEY,
          'Content-Type': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(10000), // 10 seconds timeout
      });

      console.log('Neshan API Response Status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Neshan API error:', {
          status: response.status,
          statusText: response.statusText,
          error: errorText
        });
        return null;
      }

      const data = await response.json();
      console.log('Neshan API Response Data:', data);
      console.log('Response data type:', typeof data);
      console.log('Response data keys:', Object.keys(data || {}));
      
      // Handle different response formats
      if (data.routes && data.routes.length > 0) {
        const route = data.routes[0];
        console.log('Using routes[0] format:', route);
        
        // Extract distance and duration from legs
        if (route.legs && route.legs.length > 0) {
          const leg = route.legs[0];
          const distance = leg.distance?.value || leg.distance || 0;
          const duration = leg.duration?.value || leg.duration || 0;
          
          console.log('Extracted from legs:', { distance, duration });
          
          return {
            distance,
            duration,
            legs: route.legs,
            overview_polyline: route.overview_polyline
          };
        }
        
        return route;
      } else if (data.distance && data.duration) {
        // Direct response format
        console.log('Using direct format:', { distance: data.distance, duration: data.duration });
        return {
          distance: data.distance,
          duration: data.duration,
          legs: [{
            distance: data.distance,
            duration: data.duration,
            steps: []
          }]
        };
      } else if (data.legs && data.legs.length > 0) {
        // Legs format
        console.log('Using legs format:', data.legs[0]);
        return {
          distance: data.legs[0].distance || 0,
          duration: data.legs[0].duration || 0,
          legs: data.legs
        };
      } else {
        console.warn('Unknown response format:', data);
        console.warn('Falling back to manual calculation...');
        return null;
      }
    } catch (error) {
      console.error('Error fetching route from Neshan:', error);
      
      // Fallback: calculate distance using Haversine formula
      const distance = this.calculateDistance(originLat, originLon, destLat, destLon) * 1000; // Convert to meters
      const duration = Math.round(distance / 1000 * 60); // Rough estimate: 1km per minute
      
      console.log('Using fallback calculation:', { distance, duration });
      
      return {
        distance,
        duration,
        legs: [{
          distance,
          duration,
          steps: []
        }]
      };
    }
  }

  /**
   * Open Neshan navigation with deep link support for mobile apps
   */
  static async openNeshan(options: NavigationOptions): Promise<void> {
    const { lat, lon, originLat, originLon } = options;
    
    // دریافت موقعیت کاربر اگر نداریم
    const origin = originLat && originLon 
      ? { lat: originLat, lon: originLon }
      : await this.getCurrentLocation();
    
    if (!origin) {
      // فال‌بک: فقط نمایش روی نقشه
      const webUrl = `${NESHAN_CONFIG.WEB_MAP_URL}/@${lat},${lon},15z`;
      window.open(webUrl, '_blank');
      return;
    }
    
    const routeParams = `type=car&origin=${origin.lat},${origin.lon}&destination=${lat},${lon}`;
    
    if (this.isMobileDevice()) {
      // تلاش برای باز کردن اپلیکیشن نشان
      if (this.isAndroid()) {
        // Android Deep Link
        const appUrl = `nshn://routes?${routeParams}`;
        window.location.href = appUrl;
        
        // فال‌بک به وب پس از 2 ثانیه (اگر اپ نصب نباشد)
        setTimeout(() => {
          const webUrl = `${NESHAN_CONFIG.WEB_MAP_URL}/routes?${routeParams}`;
          window.open(webUrl, '_blank');
        }, 2000);
      } else if (this.isIOS()) {
        // iOS Universal Link
        const appUrl = `neshan://routes?${routeParams}`;
        window.location.href = appUrl;
        
        // فال‌بک به وب پس از 2 ثانیه (اگر اپ نصب نباشد)
        setTimeout(() => {
          const webUrl = `${NESHAN_CONFIG.WEB_MAP_URL}/routes?${routeParams}`;
          window.open(webUrl, '_blank');
        }, 2000);
      } else {
        // سایر موبایل‌ها: مستقیم وب
        const webUrl = `${NESHAN_CONFIG.WEB_MAP_URL}/routes?${routeParams}`;
        window.open(webUrl, '_blank');
      }
    } else {
      // دسکتاپ: همیشه وب نشان
      const webUrl = `${NESHAN_CONFIG.WEB_MAP_URL}/routes?${routeParams}`;
      window.open(webUrl, '_blank');
    }
  }



  /**
   * Calculate distance between two points (Haversine formula)
   */
  static calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371; // Earth's radius in kilometers
    const dLat = this.toRad(lat2 - lat1);
    const dLon = this.toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Convert degrees to radians
   */
  private static toRad(deg: number): number {
    return deg * (Math.PI / 180);
  }

  /**
   * Format distance for display
   */
  static formatDistance(distance: number): string {
    if (distance < 1) {
      return `${Math.round(distance * 1000)} متر`;
    } else {
      return `${distance.toFixed(1)} کیلومتر`;
    }
  }

  /**
   * Estimate travel time (rough calculation)
   */
  static estimateTravelTime(distance: number, averageSpeed: number = 50): string {
    const timeInHours = distance / averageSpeed;
    const hours = Math.floor(timeInHours);
    const minutes = Math.round((timeInHours - hours) * 60);
    
    if (hours > 0) {
      return `${hours} ساعت ${minutes} دقیقه`;
    } else {
      return `${minutes} دقیقه`;
    }
  }

  /**
   * Get user's current location
   */
  static async getCurrentLocation(): Promise<{ lat: number; lon: number } | null> {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        console.error('Geolocation is not supported by this browser');
        resolve(null);
        return;
      }

      console.log('Requesting location access...');

      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log('Location received:', {
            lat: position.coords.latitude,
            lon: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
          resolve({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
        },
        (error) => {
          console.error('Geolocation error:', {
            code: error.code,
            message: error.message,
            codeDescriptions: {
              1: 'PERMISSION_DENIED',
              2: 'POSITION_UNAVAILABLE', 
              3: 'TIMEOUT'
            }
          });
          resolve(null);
        },
        {
          enableHighAccuracy: true,
          timeout: 15000, // افزایش timeout به 15 ثانیه
          maximumAge: 60000 // کاهش cache به 1 دقیقه
        }
      );
    });
  }


}

export default NavigationService;
