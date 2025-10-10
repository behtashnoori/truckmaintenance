/**
 * Neshan API Test Utility
 * برای تست مستقیم API نشان
 */

import NESHAN_CONFIG from '@/config/neshan';

export const testNeshanAPI = async () => {
  console.log('🧪 Testing Neshan API...');
  console.log('API Key:', NESHAN_CONFIG.API_KEY.substring(0, 15) + '...');
  console.log('Base URL:', NESHAN_CONFIG.API_BASE_URL);
  
  // Test coordinates (Tehran locations)
  const origin = { lat: 35.6892, lon: 51.3890 }; // Tehran center
  const destination = { lat: 35.7219, lon: 51.3347 }; // Azadi Square
  
  const testUrl = `${NESHAN_CONFIG.API_BASE_URL}/direction?type=car&origin=${origin.lat},${origin.lon}&destination=${destination.lat},${destination.lon}`;
  
  console.log('Test URL:', testUrl);
  
  try {
    const response = await fetch(testUrl, {
      method: 'GET',
      headers: {
        'Api-Key': NESHAN_CONFIG.API_KEY,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('Response Status:', response.status);
    console.log('Response Headers:', Object.fromEntries(response.headers.entries()));
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ API Response:', data);
      return { success: true, data };
    } else {
      const errorText = await response.text();
      console.error('❌ API Error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      return { success: false, error: errorText, status: response.status };
    }
  } catch (error) {
    console.error('❌ Network Error:', error);
    return { success: false, error: error.message };
  }
};

// Test different API endpoints
export const testNeshanEndpoints = async () => {
  const endpoints = [
    'https://api.neshan.org/v4/direction',
    'https://api.neshan.org/v1/direction', 
    'https://api.neshan.org/direction',
    'https://platform.neshan.org/api/v4/direction'
  ];
  
  const origin = { lat: 35.6892, lon: 51.3890 };
  const destination = { lat: 35.7219, lon: 51.3347 };
  
  for (const endpoint of endpoints) {
    console.log(`\n🔍 Testing endpoint: ${endpoint}`);
    
    const testUrl = `${endpoint}?type=car&origin=${origin.lat},${origin.lon}&destination=${destination.lat},${destination.lon}`;
    
    try {
      const response = await fetch(testUrl, {
        method: 'GET',
        headers: {
          'Api-Key': NESHAN_CONFIG.API_KEY,
          'Content-Type': 'application/json',
        },
      });
      
      console.log(`Status: ${response.status} ${response.statusText}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Success:', data);
      } else {
        const errorText = await response.text();
        console.log('❌ Error:', errorText.substring(0, 200));
      }
    } catch (error) {
      console.log('❌ Network Error:', error.message);
    }
  }
};

// Make functions available globally for console testing
if (typeof window !== 'undefined') {
  (window as any).testNeshanAPI = testNeshanAPI;
  (window as any).testNeshanEndpoints = testNeshanEndpoints;
}
