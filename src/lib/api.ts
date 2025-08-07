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
}

interface ProviderSearchResult {
  id: string;
  name: string;
  phone: string;
  address: string;
  distance_km: number;
}

type ServiceCategory = 'roadside' | 'tire' | 'recovery';

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
    name: 'تعمیرگاه رستگار',
    phone: '09123456789',
    address: 'تهران، خیابان آزادی، کیلومتر ۱۰',
    distance_km: 2.5,
    categories: ['tire', 'recovery'],
    location: { lat: 35.7219, lon: 51.3347 },
    radius_km: 50
  },
  {
    id: '2',
    name: 'خدمات جاده‌ای امداد',
    phone: '09121234567',
    address: 'تهران، بزرگراه کرج، کیلومتر ۱۵',
    distance_km: 5.2,
    categories: ['roadside', 'recovery'],
    location: { lat: 35.7419, lon: 51.3047 },
    radius_km: 75
  },
  {
    id: '3',
    name: 'مجموعه خدماتی پارس',
    phone: '09129876543',
    address: 'قم، جاده تهران، کیلومتر ۵',
    distance_km: 8.1,
    categories: ['roadside', 'tire'],
    location: { lat: 35.6719, lon: 51.2747 },
    radius_km: 60
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
    category?: ServiceCategory
  ): Promise<ApiResponse<ProviderSearchResult[]>> {
    // Mock implementation for development
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
    
    let filteredProviders = mockProviders;
    
    if (category) {
      filteredProviders = mockProviders.filter(p => p.categories.includes(category));
    }

    const results: ProviderSearchResult[] = filteredProviders.map(p => ({
      id: p.id,
      name: p.name,
      phone: p.phone,
      address: p.address,
      distance_km: p.distance_km
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
export type { Provider, ProviderSearchResult, ServiceCategory, ProviderRegistration, ContactForm };