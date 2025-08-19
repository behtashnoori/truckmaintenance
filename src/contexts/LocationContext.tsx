import React, { createContext, useContext, useState } from 'react';

export const DEFAULT_LOCATION = {
  lat: 35.7219,
  lon: 51.3347,
};

interface LocationState {
  lat: number | null;
  lon: number | null;
  isLoading: boolean;
  error: string | null;
}

interface LocationContextType extends LocationState {
  requestLocation: () => void;
  updateLocation: () => Promise<void>;
  setManualLocation: (lat: number, lon: number) => void;
  clearError: () => void;
}

const LocationContext = createContext<LocationContextType | undefined>(undefined);

export const useLocation = () => {
  const context = useContext(LocationContext);
  if (!context) {
    throw new Error('useLocation must be used within a LocationProvider');
  }
  return context;
};

interface LocationProviderProps {
  children: React.ReactNode;
}

export const LocationProvider: React.FC<LocationProviderProps> = ({ children }) => {
  const [state, setState] = useState<LocationState>({
    lat: DEFAULT_LOCATION.lat,
    lon: DEFAULT_LOCATION.lon,
    isLoading: false,
    error: null,
  });

  const requestLocation = () => {
    if (!navigator.geolocation) {
      setState(prev => ({
        ...prev,
        error: 'مرورگر شما از موقعیت جغرافیایی پشتیبانی نمی‌کند',
        isLoading: false,
      }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
          isLoading: false,
          error: null,
        });
      },
      (error) => {
        let errorMessage = 'خطا در دریافت موقعیت';
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'دسترسی به موقعیت رد شده است';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'موقعیت در دسترس نیست';
            break;
          case error.TIMEOUT:
            errorMessage = 'زمان درخواست موقعیت تمام شد';
            break;
        }

        setState(prev => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  };

  const setManualLocation = (lat: number, lon: number) => {
    setState({
      lat,
      lon,
      isLoading: false,
      error: null,
    });
  };

  const updateLocation = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        const error = 'مرورگر شما از موقعیت جغرافیایی پشتیبانی نمی‌کند';
        setState(prev => ({
          ...prev,
          error,
          isLoading: false,
        }));
        reject(new Error(error));
        return;
      }

      setState(prev => ({ ...prev, isLoading: true, error: null }));

      navigator.geolocation.getCurrentPosition(
        (position) => {
          setState({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
            isLoading: false,
            error: null,
          });
          resolve();
        },
        (error) => {
          let errorMessage = 'خطا در دریافت موقعیت';
          
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'دسترسی به موقعیت رد شده است';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'موقعیت در دسترس نیست';
              break;
            case error.TIMEOUT:
              errorMessage = 'زمان درخواست موقعیت تمام شد';
              break;
          }

          setState(prev => ({
            ...prev,
            isLoading: false,
            error: errorMessage,
          }));
          reject(new Error(errorMessage));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000,
        }
      );
    });
  };

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };
  return (
    <LocationContext.Provider
      value={{
        ...state,
        requestLocation,
        updateLocation,
        setManualLocation,
        clearError,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};