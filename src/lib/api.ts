const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

function authHeader() {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function http<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...authHeader(),
      ...(options.headers || {}),
    },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

// --- Types (حداقلی/قابل توسعه)
export type ServiceCategory = { id: number; name: string }
export type VehicleType = { id: number; name: string }

export async function requestOTP(phone: string): Promise<{ success: boolean }> {
  return http('/auth/request-otp', {
    method: 'POST',
    body: JSON.stringify({ phone }),
  })
}

export async function verifyOTP(phone: string, code: string): Promise<{ token: string }> {
  const data = await http<{ token: string }>('/auth/verify-otp', {
    method: 'POST',
    body: JSON.stringify({ phone, code }),
  })
  localStorage.setItem('token', data.token)
  return data
}

export type CreateProviderInput = {
  name: string
  phone?: string
  lat?: number
  lon?: number
  address?: string
  categories?: number[]        // IDs of ServiceCategory
  vehicle_types?: number[]     // IDs of VehicleType
  radius_km?: number
  is_24_7?: boolean
  // هر فیلد لازم دیگر را که بک‌اند می‌پذیرد اضافه کن
}

export async function createProvider(payload: CreateProviderInput): Promise<{ id: number }> {
  return http('/providers', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// نمونه‌هایی که احتمالاً جای دیگر استفاده می‌شوند:
export async function listServiceCategories(): Promise<ServiceCategory[]> {
  return http('/service-categories')
}
export async function listVehicleTypes(): Promise<VehicleType[]> {
  return http('/vehicle-types')
}
