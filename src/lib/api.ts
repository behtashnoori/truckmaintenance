// API Layer for Heavy Vehicle Service PWA
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

interface Provider {
  id: string;
  name: string;
  phone: string;
  address: string;
  distance_km: number;
  categories: ServiceCategory[];
  location: {
    lat: number;
    lon: number;
  };
  radius_km: number;
  is_24_7: boolean;
  vehicle_types: VehicleType[];
}

interface ProviderSearchResult {
  id: string;
  name: string;
  phone: string;
  address: string;
  distance_km: number;
  is_24_7: boolean;
  vehicle_types: VehicleType[];
  radius_km: number;
  categories: ServiceCategory[];
}

type ServiceCategory = 'roadside' | 'tire' | 'recovery' | 'oil';
type VehicleType = 'truck' | 'semi' | 'bus';

interface OtpRequest {
  phone: string;
}

interface OtpVerify {
  phone: string;
  code: string;
}

interface ProviderRegistration {
  name: string;
  phone: string;
  radius_km: number;
  categories: ServiceCategory[];
  is_24_7: boolean;
  vehicle_types: VehicleType[];
}

interface CompanyRegistration {
  name: string;
  phone: string;
}

interface ContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}

// Mock data for development
const mockProviders: Provider[] = [
  {
    id: '1',
    name: 'امداد جاده‌ای آریا',
    phone: '+989121234567',
    address: 'تهران–قم، کیلومتر ۲۵',
    distance_km: 3.2,
    categories: ['recovery'],
    location: { lat: 35.7219, lon: 51.3347 },
    radius_km: 60,
    is_24_7: true,
    vehicle_types: ['truck', 'semi']
  },
  {
    id: '2',
    name: 'خدمات لاستیک پارس',
    phone: '+989129876543',
    address: 'اتوبان کرج، نبش خیابان آزادی',
    distance_km: 7.8,
    categories: ['tire'],
    location: { lat: 35.7419, lon: 51.3047 },
    radius_km: 45,
    is_24_7: false,
    vehicle_types: ['truck', 'bus']
  },
  {
    id: '3',
    name: 'پارکینگ و رستوران سروش',
    phone: '+989125557890',
    address: 'جاده ساوه، کیلومتر ۱۵',
    distance_km: 12.5,
    categories: ['roadside'],
    location: { lat: 35.6719, lon: 51.2747 },
    radius_km: 30,
    is_24_7: true,
    vehicle_types: ['truck', 'semi', 'bus']
  },
  {
    id: '4',
    name: 'یدک‌کش شبانه‌روزی احمد',
    phone: '+989123456789',
    address: 'بزرگراه آزادگان، خروجی کرج',
    distance_km: 5.1,
    categories: ['recovery'],
    location: { lat: 35.6919, lon: 51.2647 },
    radius_km: 80,
    is_24_7: true,
    vehicle_types: ['truck', 'semi']
  },
  {
    id: '5',
    name: 'تعمیرگاه لاستیک شریف',
    phone: '+989127654321',
    address: 'شهر قدس، خیابان امام خمینی',
    distance_km: 8.9,
    categories: ['tire'],
    location: { lat: 35.8019, lon: 51.1547 },
    radius_km: 25,
    is_24_7: false,
    vehicle_types: ['truck']
  },
  {
    id: '6',
    name: 'مجتمع خدماتی بهشت',
    phone: '+989132223333',
    address: 'جاده اصفهان، کیلومتر ۴۵',
    distance_km: 15.2,
    categories: ['roadside'],
    location: { lat: 35.7319, lon: 51.1947 },
    radius_km: 50,
    is_24_7: true,
    vehicle_types: ['truck', 'semi', 'bus']
  },
  {
    id: '7',
    name: 'امداد سریع کامیون',
    phone: '+989111112222',
    address: 'اتوبان کرج–قزوین، استراحتگاه مهرشهر',
    distance_km: 22.0,
    categories: ['recovery'],
    location: { lat: 35.6419, lon: 51.2347 },
    radius_km: 40,
    is_24_7: false,
    vehicle_types: ['truck', 'semi']
  },
  {
    id: '8',
    name: 'لاستیک فروشی رضا',
    phone: '+989144445555',
    address: 'شهریار، میدان امام حسین',
    distance_km: 11.7,
    categories: ['tire'],
    location: { lat: 35.7519, lon: 51.2847 },
    radius_km: 35,
    is_24_7: false,
    vehicle_types: ['truck', 'bus']
  },
  {
    id: '9',
    name: 'جایگاه سوخت و پارکینگ ملی',
    phone: '+989155556666',
    address: 'آزادراه تهران–شمال، کیلومتر ۳۲',
    distance_km: 18.4,
    categories: ['roadside'],
    location: { lat: 35.7819, lon: 51.3647 },
    radius_km: 20,
    is_24_7: true,
    vehicle_types: ['truck', 'semi', 'bus']
  },
  {
    id: '10',
    name: 'خدمات اتوبوسی آسمان',
    phone: '+989166667777',
    address: 'ورامین، خیابان شهید بهشتی',
    distance_km: 25.3,
    categories: ['roadside', 'tire'],
    location: { lat: 35.6119, lon: 51.3947 },
    radius_km: 55,
    is_24_7: false,
    vehicle_types: ['bus']
  },
  {
    id: '11',
    name: 'روغن فروشی تهران',
    phone: '+989177788899',
    address: 'تهران، خیابان انقلاب',
    distance_km: 4.2,
    categories: ['oil'],
    location: { lat: 35.6892, lon: 51.3890 },
    radius_km: 30,
    is_24_7: false,
    vehicle_types: ['truck', 'semi']
  },
  {
    id: '12',
    name: 'فروشگاه فیلتر اصفهان',
    phone: '+989188899900',
    address: 'اصفهان، میدان نقش جهان',
    distance_km: 3.5,
    categories: ['oil'],
    location: { lat: 32.6539, lon: 51.6660 },
    radius_km: 25,
    is_24_7: true,
    vehicle_types: ['truck']
  }
];

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('API Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'خطای ناشناخته',
      };
    }
  }

  // Search providers by location and category
  async searchProviders(
    lat: number,
    lon: number,
    category?: ServiceCategory,
    vehicle?: VehicleType
  ): Promise<ApiResponse<ProviderSearchResult[]>> {
    // Mock implementation for development
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    
    let filteredProviders = mockProviders;

    if (category) {
      filteredProviders = filteredProviders.filter(p => p.categories.includes(category));
    }

    if (vehicle) {
      filteredProviders = filteredProviders.filter(p => p.vehicle_types.includes(vehicle));
    }

    const toRad = (value: number) => (value * Math.PI) / 180;
    const calcDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
      const R = 6371; // km
      const dLat = toRad(lat2 - lat1);
      const dLon = toRad(lon2 - lon1);
      const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return R * c;
    };

    filteredProviders = filteredProviders
      .map(p => ({
        ...p,
        distance_km: calcDistance(lat, lon, p.location.lat, p.location.lon)
      }))
      .filter(p => p.distance_km <= p.radius_km)
      .sort((a, b) => a.distance_km - b.distance_km);

    const results: ProviderSearchResult[] = filteredProviders.map(p => ({
      id: p.id,
      name: p.name,
      phone: p.phone,
      address: p.address,
      distance_km: Math.round(p.distance_km * 10) / 10,
      is_24_7: p.is_24_7,
      vehicle_types: p.vehicle_types,
      radius_km: p.radius_km,
      categories: p.categories
    }));

    return { success: true, data: results };
  }

  // Get provider details
  async getProvider(id: string): Promise<ApiResponse<Provider>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const provider = mockProviders.find(p => p.id === id);
    if (!provider) {
      return { success: false, error: 'ارائه‌دهنده یافت نشد' };
    }

    return { success: true, data: provider };
  }

  // Request OTP for phone verification
  async requestOtp(phone: string): Promise<ApiResponse<{ success: boolean }>> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/request-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return { success: false, error: err.error || res.statusText };
      }
      return { success: true, data: { success: true } };
    } catch {
      return { success: false, error: 'network_error' };
    }
  }

  // Verify OTP code
  async verifyOtp(
    phone: string,
    code: string
  ): Promise<ApiResponse<{ token: string }>> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, code }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return { success: false, error: err.error || res.statusText };
      }
      const data = await res.json();
      return { success: true, data };
    } catch {
      return { success: false, error: 'network_error' };
    }
  }

  // Register company information
  async registerCompany(
    data: CompanyRegistration,
    token: string
  ): Promise<ApiResponse<{ id: string }>> {
    try {
      const res = await fetch(`${API_BASE_URL}/providers/company`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        return { success: false, error: err.error || res.statusText };
      }
      const result = await res.json();
      return { success: true, data: result };
    } catch {
      return { success: false, error: 'network_error' };
    }
  }

  // Register new provider
  async registerProvider(
    data: ProviderRegistration,
    token: string
  ): Promise<ApiResponse<{ status: string }>> {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return { success: true, data: { status: 'pending' } };
  }

  // Submit contact form
  async submitContact(data: ContactForm): Promise<ApiResponse<{ success: boolean }>> {
    await new Promise(resolve => setTimeout(resolve, 600));
    
    return { success: true, data: { success: true } };
  }
}

export const api = new ApiClient();

// Export convenience functions for direct use
export const getProviders = (lat: number, lon: number, category?: ServiceCategory, vehicle?: VehicleType) => 
  api.searchProviders(lat, lon, category, vehicle);

export const getProvider = (id: string) => api.getProvider(id);

export const requestOTP = (phone: string) => api.requestOtp(phone);

export const verifyOTP = (phone: string, code: string) =>
  api.verifyOtp(phone, code);

export const createCompany = (data: CompanyRegistration, token: string) =>
  api.registerCompany(data, token);

export const createProvider = (data: ProviderRegistration, token?: string) =>
  api.registerProvider(data, token || 'mock-token');

export const submitContactForm = (data: ContactForm) => api.submitContact(data);

export type {
  Provider,
  ProviderSearchResult,
  ServiceCategory,
  VehicleType,
  ProviderRegistration,
  CompanyRegistration,
  ContactForm,
};
