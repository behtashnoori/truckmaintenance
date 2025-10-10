/**
 * Neshan Map Service Configuration
 */

export const NESHAN_CONFIG = {
  // API Key from environment variable or fallback
  API_KEY: import.meta.env.VITE_NESHAN_API_KEY || 'service.d39f79de30c34282b0a48564ff3b8b13',
  
  // API Endpoints
  API_BASE_URL: 'https://api.neshan.org/v4',
  ROUTING_URL: 'https://api.neshan.org/v4/direction',
  
  // Web URLs
  WEB_BASE_URL: 'https://neshan.org',
  WEB_MAP_URL: 'https://neshan.org/maps',
  
  // Default settings
  DEFAULT_ZOOM: 15,
  DEFAULT_VEHICLE_TYPE: 'car', // car, motorcycle, taxi
};

export default NESHAN_CONFIG;

