// API Layer for Heavy Vehicle Service PWA
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

interface ApiResponse<T = any> {
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
}

type ServiceCategory = 'roadside' | 'tire' | 'recovery';
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
  location: {
    lat: number;
    lon: number;
  };
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

interface RoadsideFacility {
  id: string;
  name: string;
  type: 'restaurant' | 'fuel' | 'parking';
  address: string;
  location: {
    lat: number;
    lon: number;
  };
  distance_km: number;
}

// Mock data for development
const mockProviders: Provider[] = [
  {
    id: '1',
    name: 'تعمیرگاه رستگار',
    phone: '09123456789',
    address: 'تهران، خیابان آزادی، کیلومتر ۱۰',
    distance_km: 2.5,
    categories: ['tire', 'recovery'],
    location: { lat: 35.7219, lon: 51.3347 },
    radius_km: 50,
    is_24_7: true,
    vehicle_types: ['truck', 'semi']
  },
  {
    id: '2',
    name: 'خدمات جاده‌ای امداد',
    phone: '09121234567',
    address: 'تهران، بزرگراه کرج، کیلومتر ۱۵',
    distance_km: 5.2,
    categories: ['roadside', 'recovery'],
    location: { lat: 35.7419, lon: 51.3047 },
    radius_km: 75,
    is_24_7: false,
    vehicle_types: ['truck', 'bus']
  },
  {
    id: '3',
    name: 'مجموعه خدماتی پارس',
    phone: '09129876543',
    address: 'قم، جاده تهران، کیلومتر ۵',
    distance_km: 8.1,
    categories: ['roadside', 'tire'],
    location: { lat: 35.6719, lon: 51.2747 },
    radius_km: 60,
    is_24_7: true,
    vehicle_types: ['truck', 'semi', 'bus']
  },
  {
    id: '4',
    name: 'سرویس تخصصی اتوبوس',
    phone: '09191234567',
    address: 'اصفهان، خیابان چهارباغ، پلاک ۱۲۳',
    distance_km: 12.3,
    categories: ['roadside', 'tire'],
    location: { lat: 35.6919, lon: 51.2647 },
    radius_km: 40,
    is_24_7: false,
    vehicle_types: ['bus']
  },
  {
    id: '5',
    name: 'تریلی سرویس البرز',
    phone: '09361234567',
    address: 'کرج، خیابان طالقانی، کیلومتر ۸',
    distance_km: 18.7,
    categories: ['recovery', 'tire'],
    location: { lat: 35.8019, lon: 51.1547 },
    radius_km: 80,
    is_24_7: true,
    vehicle_types: ['semi']
  }
];

const mockRoadsideFacilities: Omit<RoadsideFacility, 'distance_km'>[] = [
  {
    id: 'r1',
    name: 'رستوران بهار',
    type: 'restaurant',
    address: 'تهران، خیابان آزادی',
    location: { lat: 35.7225, lon: 51.337 },
  },
  {
    id: 'f1',
    name: 'پمپ بنزین آزادی',
    type: 'fuel',
    address: 'تهران، بزرگراه شهید لشگری',
    location: { lat: 35.7249, lon: 51.33 },
  },
  {
    id: 'p1',
    name: 'پارکینگ کامیونداران',
    type: 'parking',
    address: 'تهران، جاده مخصوص',
    location: { lat: 35.73, lon: 51.35 },
  },
];

function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

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

    const results: ProviderSearchResult[] = filteredProviders.map(p => ({
      id: p.id,
      name: p.name,
      phone: p.phone,
      address: p.address,
      distance_km: p.distance_km,
      is_24_7: p.is_24_7,
      vehicle_types: p.vehicle_types,
      radius_km: p.radius_km
    }));

    return { success: true, data: results };
  }

  // Search nearby roadside facilities like restaurants, fuel and parking
  async searchRoadsideFacilities(
    lat: number,
    lon: number
  ): Promise<ApiResponse<RoadsideFacility[]>> {
    await new Promise(resolve => setTimeout(resolve, 300));

    const facilities: RoadsideFacility[] = mockRoadsideFacilities.map(f => ({
      ...f,
      distance_km: calculateDistance(lat, lon, f.location.lat, f.location.lon),
    }));

    facilities.sort((a, b) => a.distance_km - b.distance_km);
    return { success: true, data: facilities };
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

export const getRoadsideFacilities = (lat: number, lon: number) =>
  api.searchRoadsideFacilities(lat, lon);

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
  RoadsideFacility,
};