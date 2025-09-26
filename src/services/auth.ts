/**
 * Authentication service for managing JWT tokens and user sessions
 */

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'business_expert' | 'support';
  is_active: boolean;
}

interface LoginResponse {
  message: string;
  token: string;
  user: User;
}

class AuthService {
  private token: string | null = null;
  private user: User | null = null;

  constructor() {
    this.loadFromStorage();
  }

  /**
   * Load token and user from localStorage
   */
  private loadFromStorage(): void {
    this.token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('auth_user');
    if (userStr) {
      try {
        this.user = JSON.parse(userStr);
      } catch (e) {
        console.error('Error parsing user data:', e);
        this.clearAuth();
      }
    }
  }

  /**
   * Save token and user to localStorage
   */
  private saveToStorage(token: string, user: User): void {
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(user));
  }

  /**
   * Clear authentication data
   */
  private clearAuth(): void {
    this.token = null;
    this.user = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  }

  /**
   * Login user with username and password
   */
  async login(username: string, password: string): Promise<LoginResponse> {
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Login failed');
      }

      const data: LoginResponse = await response.json();
      
      this.token = data.token;
      this.user = data.user;
      this.saveToStorage(data.token, data.user);

      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      if (this.token) {
        await fetch('/api/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuth();
    }
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    return this.user;
  }

  /**
   * Get current token
   */
  getToken(): string | null {
    return this.token;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.token !== null && this.user !== null;
  }

  /**
   * Check if user has specific role
   */
  hasRole(role: string): boolean {
    return this.user?.role === role;
  }

  /**
   * Check if user is admin
   */
  isAdmin(): boolean {
    return this.hasRole('admin');
  }

  /**
   * Check if user is business expert
   */
  isBusinessExpert(): boolean {
    return this.hasRole('business_expert') || this.isAdmin();
  }

  /**
   * Get authorization header for API calls
   */
  getAuthHeader(): { Authorization: string } | {} {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  /**
   * Refresh user data from server
   */
  async refreshUser(): Promise<User | null> {
    try {
      if (!this.token) {
        return null;
      }

      const response = await fetch('/api/me', {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          this.clearAuth();
          return null;
        }
        throw new Error('Failed to refresh user data');
      }

      const user: User = await response.json();
      this.user = user;
      this.saveToStorage(this.token, user);
      
      return user;
    } catch (error) {
      console.error('Error refreshing user:', error);
      this.clearAuth();
      return null;
    }
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(): boolean {
    if (!this.token) return true;
    
    try {
      const payload = JSON.parse(atob(this.token.split('.')[1]));
      const exp = payload.exp * 1000; // Convert to milliseconds
      return Date.now() >= exp;
    } catch (e) {
      return true;
    }
  }

  /**
   * Auto-refresh token if needed
   */
  async ensureValidToken(): Promise<boolean> {
    if (!this.isAuthenticated()) {
      return false;
    }

    if (this.isTokenExpired()) {
      this.clearAuth();
      return false;
    }

    return true;
  }
}

// Export singleton instance
export const authService = new AuthService();
export type { User, LoginResponse };
