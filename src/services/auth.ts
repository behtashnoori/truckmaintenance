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
  private sessionStartTime: number = 0;
  private lastActivityTime: number = 0;

  constructor() {
    this.loadFromStorage();
  }

  /**
   * Load token and user from localStorage
   */
  private loadFromStorage(): void {
    this.token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('auth_user');
    const sessionStartStr = localStorage.getItem('auth_session_start');
    const lastActivityStr = localStorage.getItem('auth_last_activity');
    
    if (userStr) {
      try {
        this.user = JSON.parse(userStr);
      } catch (e) {
        console.error('Error parsing user data:', e);
        this.clearAuth();
      }
    }
    
    if (sessionStartStr) {
      this.sessionStartTime = parseInt(sessionStartStr, 10);
    }
    
    if (lastActivityStr) {
      this.lastActivityTime = parseInt(lastActivityStr, 10);
    }
  }

  /**
   * Save token and user to localStorage
   */
  private saveToStorage(token: string, user: User): void {
    const now = Date.now();
    localStorage.setItem('auth_token', token);
    localStorage.setItem('auth_user', JSON.stringify(user));
    localStorage.setItem('auth_session_start', now.toString());
    localStorage.setItem('auth_last_activity', now.toString());
    this.sessionStartTime = now;
    this.lastActivityTime = now;
  }

  /**
   * Clear authentication data
   */
  private clearAuth(): void {
    this.token = null;
    this.user = null;
    this.sessionStartTime = 0;
    this.lastActivityTime = 0;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_session_start');
    localStorage.removeItem('auth_last_activity');
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

  /**
   * Start a new session
   */
  startSession(): void {
    const now = Date.now();
    this.sessionStartTime = now;
    this.lastActivityTime = now;
    localStorage.setItem('auth_session_start', now.toString());
    localStorage.setItem('auth_last_activity', now.toString());
  }

  /**
   * End current session
   */
  endSession(): void {
    this.sessionStartTime = 0;
    this.lastActivityTime = 0;
    localStorage.removeItem('auth_session_start');
    localStorage.removeItem('auth_last_activity');
  }

  /**
   * Update last activity time
   */
  updateActivity(): void {
    const now = Date.now();
    this.lastActivityTime = now;
    localStorage.setItem('auth_last_activity', now.toString());
  }

  /**
   * Get session duration in milliseconds
   */
  getSessionDuration(): number {
    if (this.sessionStartTime === 0) {
      return 0;
    }
    return Date.now() - this.sessionStartTime;
  }

  /**
   * Get time since last activity in milliseconds
   */
  getTimeSinceLastActivity(): number {
    if (this.lastActivityTime === 0) {
      return 0;
    }
    return Date.now() - this.lastActivityTime;
  }

  /**
   * Validate current session (client-side check)
   */
  async validateSession(): Promise<boolean> {
    if (!this.isAuthenticated()) {
      return false;
    }

    if (this.isTokenExpired()) {
      this.clearAuth();
      return false;
    }

    // Update activity time on validation
    this.updateActivity();
    return true;
  }

  /**
   * Validate session with server (server-side check)
   */
  async validateSessionWithServer(): Promise<boolean> {
    if (!this.token) {
      return false;
    }

    try {
      const response = await fetch('/api/validate-session', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          this.clearAuth();
          return false;
        }
        return false;
      }

      const data = await response.json();
      
      if (!data.valid) {
        this.clearAuth();
        return false;
      }

      // Update activity time on successful validation
      this.updateActivity();
      return true;

    } catch (error) {
      console.error('Session validation error:', error);
      return false;
    }
  }

  /**
   * Get formatted session duration
   */
  getFormattedSessionDuration(): string {
    const duration = this.getSessionDuration();
    const hours = Math.floor(duration / (60 * 60 * 1000));
    const minutes = Math.floor((duration % (60 * 60 * 1000)) / (60 * 1000));
    
    if (hours > 0) {
      return `${hours} ساعت ${minutes} دقیقه`;
    } else {
      return `${minutes} دقیقه`;
    }
  }

  /**
   * Get session information
   */
  getSessionInfo() {
    return {
      sessionStartTime: this.sessionStartTime,
      lastActivityTime: this.lastActivityTime,
      sessionDuration: this.getSessionDuration(),
      timeSinceLastActivity: this.getTimeSinceLastActivity(),
      formattedSessionDuration: this.getFormattedSessionDuration(),
      isSessionActive: this.sessionStartTime > 0,
    };
  }
}

// Export singleton instance
export const authService = new AuthService();
export type { User, LoginResponse };
