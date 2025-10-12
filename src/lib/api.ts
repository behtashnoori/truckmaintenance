// API Layer for Heavy Vehicle Service PWA
import { apiFetch } from '../utils/api';

interface ApiError {
  code?: string;
  message: string;
  action?: string;
  support_contact?: string;
  details?: string;
  retry_after?: number;
  max_attempts?: number;
}

interface ApiWarning {
  code?: string;
  message: string;
  note?: string;
}

interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string | ApiError;
  warning?: ApiWarning;
  message?: string;
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

interface LocationOption {
  name: string;
  lat: number;
  lon: number;
  type: 'province' | 'city';
}

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

interface ProviderApplicationInput {
  companyName: string;
  representativeFirstName: string;
  representativeLastName: string;
  address: string;
  phoneMobile: string;
  phoneLandline?: string;
  serviceCategories: string[]; // Array of category names
  latitude?: number;
  longitude?: number;
}

interface ContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}


class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const data = await apiFetch<T>(endpoint, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });
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
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lon.toString(),
    });
    
    if (category) {
      params.append('category', category);
    }
    
    if (vehicle) {
      params.append('vehicle', vehicle);
    }

    return this.request<ProviderSearchResult[]>(`/api/public/providers?${params}`, {
      method: 'GET',
    });
  }

  // Get provider details
  async getProvider(id: string): Promise<ApiResponse<Provider>> {
    return this.request<Provider>(`/api/public/providers/${id}`, {
      method: 'GET',
    });
  }

  // Request OTP for phone verification
  async requestOtp(phone: string): Promise<ApiResponse<{ success: boolean }>> {
    return this.request<{ success: boolean }>('/auth/request-otp', {
      method: 'POST',
      body: JSON.stringify({ phone }),
    });
  }

  // Verify OTP code
  async verifyOtp(phone: string, code: string): Promise<ApiResponse<{ token: string }>> {
    return this.request<{ token: string }>('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ phone, code }),
    });
  }

  // Register new provider
  async registerProvider(
    data: ProviderRegistration,
    token: string
  ): Promise<ApiResponse<{ status: string }>> {
    return this.request<{ status: string }>('/provider-registration', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });
  }

  // Submit provider application with enhanced error handling
  async submitProviderApplication(
    data: ProviderApplicationInput
  ): Promise<ApiResponse<{ id: number; status: string }>> {
    try {
      const response = await fetch(`/api/provider-applications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      // Handle different response statuses
      if (response.ok) {
        return {
          success: true,
          data: result.data,
          message: result.message,
          warning: result.warning, // Include fuzzy match warning
        };
      } else {
        // Return structured error
        return {
          success: false,
          error: result.error || result.message || 'خطا در ارسال درخواست',
        };
      }
    } catch (error) {
      console.error('API Error:', error);
      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: 'خطا در ارتباط با سرور. لطفاً اتصال اینترنت خود را بررسی کنید.',
        },
      };
    }
  }

  // Submit contact form
  async submitContact(data: ContactForm): Promise<ApiResponse<{ success: boolean }>> {
    return this.request<{ success: boolean }>('/contact', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Get locations (provinces and cities)
  async getLocations(): Promise<ApiResponse<LocationOption[]>> {
    return this.request<LocationOption[]>('/api/public/locations', {
      method: 'GET',
    });
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

export const submitProviderApplication = (data: ProviderApplicationInput) => api.submitProviderApplication(data);

export type {
  Provider,
  ProviderSearchResult,
  ServiceCategory,
  VehicleType,
  ProviderRegistration,
  ProviderApplicationInput,
  ContactForm,
  ApiError,
  ApiWarning,
  ApiResponse,
};
