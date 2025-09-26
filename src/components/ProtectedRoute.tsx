import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authService, User } from '@/services/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'business_expert' | 'support';
  fallbackPath?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  fallbackPath = '/'
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const location = useLocation();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check if user is authenticated
        if (!authService.isAuthenticated()) {
          setIsLoading(false);
          return;
        }

        // Check if token is expired
        if (authService.isTokenExpired()) {
          authService.logout();
          setIsLoading(false);
          return;
        }

        // Refresh user data
        const currentUser = await authService.refreshUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Auth check error:', error);
        authService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>در حال بررسی احراز هویت...</p>
        </div>
      </div>
    );
  }

  // Check if user is authenticated
  if (!authService.isAuthenticated() || !user) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  // Check role requirement
  if (requiredRole) {
    if (requiredRole === 'admin' && !authService.isAdmin()) {
      return <Navigate to={fallbackPath} replace />;
    }
    if (requiredRole === 'business_expert' && !authService.isBusinessExpert()) {
      return <Navigate to={fallbackPath} replace />;
    }
    if (requiredRole === 'support' && !authService.hasRole('support')) {
      return <Navigate to={fallbackPath} replace />;
    }
  }

  return <>{children}</>;
};
