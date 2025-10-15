/**
 * Categories Service
 * Centralized category fetching with versioned localStorage cache
 */

export interface UICategory {
  id: string;
  title: string;
  description: string;
  originalName: string;
}

// App version for cache invalidation
const APP_VERSION = '1.0.1';
const LS_KEY = `app:${APP_VERSION}:categories`;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

interface CachedData {
  data: UICategory[];
  timestamp: number;
}

/**
 * Get categories from API with versioned cache
 */
export async function getCategories(): Promise<UICategory[]> {
  // 1) Try to read from versioned localStorage
  const cached = localStorage.getItem(LS_KEY);
  if (cached) {
    try {
      const parsed: CachedData = JSON.parse(cached);
      const now = Date.now();
      
      // Check if cache is still valid
      if (now - parsed.timestamp < CACHE_TTL) {
        console.log('Categories: Using cached data');
        return parsed.data;
      }
    } catch (error) {
      console.warn('Categories: Invalid cached data, clearing');
      localStorage.removeItem(LS_KEY);
    }
  }

  // 2) Fetch from API
  try {
    console.log('Categories: Fetching from API');
    const response = await fetch('/api/public/categories', {
      headers: {
        'Cache-Control': 'no-store',
        'Pragma': 'no-cache'
      }
    });

    if (!response.ok) {
      console.error('Categories: API error', response.status);
      return [];
    }

    const json = await response.json();
    const items: UICategory[] = (json?.data || []).map((cat: any) => ({
      id: String(cat.name).toLowerCase().replace(/\s+/g, '-'),
      title: cat.name,
      description: `${cat.companies_count || 0} ارائه‌دهنده`,
      originalName: cat.name,
    }));

    // 3) Store in versioned cache
    const cacheData: CachedData = {
      data: items,
      timestamp: Date.now()
    };
    localStorage.setItem(LS_KEY, JSON.stringify(cacheData));
    
    console.log('Categories: Fetched and cached', items.length, 'items');
    return items;
  } catch (error) {
    console.error('Categories: Fetch error', error);
    return [];
  }
}

/**
 * Clear all old versioned cache entries
 */
export function clearOldCache(): void {
  const keys = Object.keys(localStorage);
  const oldKeys = keys.filter(key => 
    key.startsWith('app:') && 
    key.includes(':categories') && 
    key !== LS_KEY
  );
  
  oldKeys.forEach(key => {
    localStorage.removeItem(key);
    console.log('Categories: Cleared old cache', key);
  });
}

/**
 * Force refresh categories (bypass cache)
 */
export async function refreshCategories(): Promise<UICategory[]> {
  localStorage.removeItem(LS_KEY);
  return getCategories();
}
