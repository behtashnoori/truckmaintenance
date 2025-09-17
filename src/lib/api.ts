// API Layer for Heavy Vehicle Service PWA

const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '');
const ensureLeadingSlash = (value: string) => (value.startsWith('/') ? value : `/${value}`);

export const API_BASE = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE) {
  console.error('VITE_API_BASE_URL is not defined');
}

const extractErrorMessage = (payload: unknown, fallback: string) => {
  if (!payload) return fallback;

  if (typeof payload === 'string') {
    return payload.trim() || fallback;
  }

  if (typeof payload === 'object') {
    const messageLike =
      // @ts-expect-error index signature not declared on purpose
      payload?.message ?? payload?.detail ?? payload?.error ?? payload?.errors;
    if (Array.isArray(messageLike)) {
      return messageLike.map(item => (typeof item === 'string' ? item : '')).join('\n') || fallback;
    }
    if (messageLike) {
      return String(messageLike);
    }
  }

  return fallback;
};

const normalizeBase = () => (API_BASE ? trimTrailingSlash(API_BASE) : null);

export async function apiFetch<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const base = normalizeBase();
  if (!base) {
    const message = 'Cannot perform request because VITE_API_BASE_URL is not defined';
    console.error(message);
    throw new Error(message);
  }

  const normalizedPath = ensureLeadingSlash(path);
  console.log('API BASE:', base, 'PATH:', normalizedPath);

  const headers = new Headers(init?.headers ?? {});
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${base}${normalizedPath}`, {
    ...init,
    headers,
  });

  const contentType = response.headers.get('content-type') ?? '';
  const expectsJson = contentType.includes('application/json');

  let payload: unknown = undefined;
  if (response.status !== 204) {
    try {
      if (expectsJson) {
        payload = await response.json();
      } else {
        const text = await response.text();
        payload = text ? text : undefined;
      }
    } catch (error) {
      console.error('Failed to parse API response', error);
    }
  }

  if (!response.ok) {
    const fallbackMessage = `HTTP ${response.status} ${response.statusText}`;
    throw new Error(extractErrorMessage(payload, fallbackMessage));
  }

  return (payload as T) ?? (undefined as T);
}

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
      const data = await apiFetch<T>(endpoint, options);
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
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Mock success response
    return { success: true, data: { success: true } };
  }

  // Verify OTP code
  async verifyOtp(phone: string, code: string): Promise<ApiResponse<{ token: string }>> {
    await new Promise(resolve => setTimeout(resolve, 600));

    // Mock verification - accept any 6-digit code
    if (code.length === 6) {
      return { success: true, data: { token: 'mock-jwt-token' } };
    }

    return { success: false, error: 'کد تأیید نامعتبر است' };
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

export const verifyOTP = (phone: string, code: string) => api.verifyOtp(phone, code);

export const createProvider = (data: ProviderRegistration, token?: string) =>
  api.registerProvider(data, token || 'mock-token');

export const submitContactForm = (data: ContactForm) => api.submitContact(data);

export type {
  Provider,
  ProviderSearchResult,
  ServiceCategory,
  VehicleType,
  ProviderRegistration,
  ContactForm,
};
